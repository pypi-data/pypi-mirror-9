import functools
import json
import logging
import pprint
import sys
import traceback

from docopt import docopt, DocoptExit
from slacker import Slacker
import websocket

from _version import __version__


def help(opts, bot, _):
    """Usage: help [<command>]

    With no arguments, print the form of all supported commands.
    With an argument, print a detailed explanation of a command.
    """
    command = opts['<command>']
    if command is None:
        return bot.help_text()

    if command not in bot.commands:
        return "%r is not a known command" % command

    return bot.commands[command].__doc__


class _CommandMeta(type):
    """
    If the commands dict is a class field on Bot, then all subclasses will share one registry.

    This metaclass initializes a separate registry on each class.
    """

    def __new__(cls, name, bases, dct):
        new_cls = super(_CommandMeta, cls).__new__(cls, name, bases, dct)
        new_cls.commands = {}

        return new_cls


class Bot(object):
    """
    A Bot connects to Slack using the `RTM API <https://api.slack.com/rtm>`__
    and responds to public messages that are directed to it with username-
    or at-mentions.

    Manage the Bot's channels in Slack itself with the `/join` command.
    A Bot can be in multiple Slack channels (though state is not isolated by channel).
    """

    __metaclass__ = _CommandMeta

    @classmethod
    def command(cls, func):
        """
        A decorator to convert a function to a command.

        Command functions should have a docopt-usage string in their docstring
        and receive three arguments:

          * opts: the docopt-parsd
          * bot: the Bot instance handling the command (eg for storing state between commands)
          * event: the Slack event that triggered the command (eg for finding the message's sender)
        """
        # adapted from https://github.com/docopt/docopt/blob/master/examples/interactive_example.py
        @functools.wraps(func)
        def _cmd_wrapper(rest, *args, **kwargs):
            try:
                usage = _cmd_wrapper.__doc__.partition('\n')[0]
                opts = docopt(usage, rest)
            except (SystemExit, DocoptExit) as e:
                # opts did not match
                return str(e)

            return func(opts, *args, **kwargs)

        cls.commands[func.__name__] = _cmd_wrapper

        return _cmd_wrapper

    @classmethod
    def help_text(cls):
        """Return a slack-formatted list of commands with their usage."""
        docs = [cmd_func.__doc__ for cmd_func in cls.commands.values()]

        # Don't want to include 'usage: ' or explanation.
        usage_lines = [doc.partition('\n')[0] for doc in docs]
        terse_lines = [line[len('Usage: '):] for line in usage_lines]
        terse_lines.sort()
        return '\n'.join(['Available commands:\n'] + terse_lines)

    def __init__(self, slack_token, config):
        """
        Do not override this to perform implementation-specific setup;
        use :func:`prepare_bot` instead.

        No IO will be done until :func:`run_forever` is called (unless :func:`prepare_bot`
        is overridden to perform some).

        :param slack_token: a Slack api token.
        :param config: an arbitrary dictionary for implementation-specific configuration.
          The same object is stored as the `config` attribute and passed to prepare methods.
        """
        #: the same config dictionary passed to init.
        self.config = config
        self._current_message_id = 0

        #: a Logger (``logging.getLogger(__name__)``).
        self.log = logging.getLogger(__name__)

        # This doesn't perform IO.
        #: a `Slacker <https://github.com/os/slacker>`__ instance created with `slack_token`.
        self.slack = Slacker(slack_token)

        #: the bot's Slack id.
        #: Not available until :func:`prepare_connection`.
        self.id = None

        #: the bot's Slack name.
        #: Not available until :func:`prepare_connection`.
        self.name = None

        #: the bot's Slack mention, equal to ``<@%s> % self.id`` .
        #: Not available until :func:`prepare_connection`.
        self.my_mention = None

        #: a `WebSocketApp <https://github.com/liris/websocket-client>`__ instance.
        #: Not available until :func:`prepare_connection`.
        self.ws = None

        self.prepare_bot(self.config)

    def prepare_bot(self, config):
        """
        Override to perform implementation-specific setup.

        This is called once by :func:`__init__` and is not called on connection restarts.
        """
        pass

    def prepare_connection(self, config):
        """
        Override to perform per-connection setup.

        This is called by run_forever and on connection restarts.
        """
        pass

    def run_forever(self):
        """Run the bot, blocking forever."""
        res = self.slack.rtm.start()
        self.log.info("current channels: %s",
                      ','.join(c['name'] for c in res.body['channels']
                               if c['is_member']))
        self.id = res.body['self']['id']
        self.name = res.body['self']['name']
        self.my_mention = "<@%s>" % self.id

        self.ws = websocket.WebSocketApp(
            res.body['url'],
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open)
        self.prepare_connection(self.config)
        self.ws.run_forever()

    def _sent_to_me(self, message):
        """Return True if this message is addressed to the bot.

        :param message: a message dict from the slack api.
        """

        text = message['text']
        my_prefixes = ["%s:" % item
                       for item in [self.name, self.my_mention]]

        if any(text.startswith(prefix) for prefix in my_prefixes):
            self.log.debug("sent to me:\n%s", pprint.pformat(message))
            return True

        return False

    def _send_message(self, channel_id, text):
        """Send a Slack message to a channel.

        :param channel_id: a slack channel id.
        :param text: a slack message. Serverside formatting is done
          in a similar way to normal user message; see
          `Slack's docs <https://api.slack.com/docs/formatting>`__.
        """

        message = {
            'id': self._current_message_id,
            'type': 'message',
            'channel': channel_id,
            'text': text,
        }
        self.ws.send(json.dumps(message))

        self._current_message_id += 1

    # Websocket callbacks.
    def _on_message(self, ws, raw_event):
        try:
            event = json.loads(raw_event)
            if 'type' not in event or event['type'] != 'message':
                return

            if 'text' not in event:
                # These are mostly changed messages, which we don't respond to right now.
                return

            if not self._sent_to_me(event):
                return

            body = event['text'].partition(':')[2].strip()
            cmd, _, rest = body.partition(' ')

            if cmd in self.commands:
                try:
                    res = self.commands[cmd](rest, self, event)
                except Exception as e:
                    self.log.exception("%s while handling %r", e, body)

                    # Send the exception and the final line of the traceback.
                    # TODO this doesn't always pick out the right line.
                    t, v, tb = sys.exc_info()
                    res = ''.join(traceback.format_exception_only(t, v))
                    tb_entries = traceback.extract_tb(tb, 3)
                    res += ''.join(traceback.format_list(tb_entries[2:]))

                self._send_message(event['channel'], res)
            else:
                self._send_message(event['channel'], "Unrecognized command.\n%s" % self.help_text())

        except Exception as e:
            # websocket-client swallows exceptions in callbacks
            self.log.exception("%s during _on_message. event:\n%s", e, pprint.pformat(raw_event))

    def _on_error(self, ws, error):
        self.log.error(error)

    def _on_close(self, ws, code, reason):
        self.log.warning("websocket closed. code: %r, reason: %r", code, reason)

        # Attempt to reconnect.
        # No need to reset _current_message_id: slack just requires ids that are unique per session.
        self.run_forever()

    def _on_open(self, ws):
        self.log.info("websocket opened")
