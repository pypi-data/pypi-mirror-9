"""
Twisted protocol and communication implementations for IRC
"""
import time

from collections import defaultdict

import smokesignal

from twisted.internet import protocol, reactor
from twisted.words.protocols import irc

from helga import settings, log
from helga.plugins import registry
from helga.util import encodings


logger = log.getLogger(__name__)


class Factory(protocol.ClientFactory):
    """
    The client factory for twisted. Ensures that a client is properly created and handles
    auto reconnect if helga is configured for it (see settings :data:`~helga.settings.AUTO_RECONNECT`
    and :data:`~helga.settings.AUTO_RECONNECT_DELAY`)
    """

    def buildProtocol(self, address):
        """
        Build the helga protocol for twisted, or in other words, create the client
        object and return it.

        :param address: an implementation of :class:`twisted.internet.interfaces.IAddress`
        :returns: an instance of :class:`helga.comm.Client`
        """
        logger.debug('Constructing Helga protocol')
        return Client(factory=self)

    def clientConnectionLost(self, connector, reason):
        """
        Handler for when the IRC connection is lost. Handles auto reconnect if helga
        is configured for it (see settings :data:`~helga.settings.AUTO_RECONNECT` and
        :data:`~helga.settings.AUTO_RECONNECT_DELAY`)
        """
        logger.info('Connection to server lost: %s', reason)

        # FIXME: Max retries
        if getattr(settings, 'AUTO_RECONNECT', True):
            delay = getattr(settings, 'AUTO_RECONNECT_DELAY', 5)
            reactor.callLater(delay, connector.connect)
        else:
            raise reason

    def clientConnectionFailed(self, connector, reason):
        """
        Handler for when the IRC connection fails. Handles auto reconnect if helga
        is configured for it (see settings :data:`~helga.settings.AUTO_RECONNECT` and
        :data:`~helga.settings.AUTO_RECONNECT_DELAY`)
        """
        logger.warning('Connection to server failed: %s', reason)

        # FIXME: Max retries
        if getattr(settings, 'AUTO_RECONNECT', True):
            delay = getattr(settings, 'AUTO_RECONNECT_DELAY', 5)
            reactor.callLater(delay, connector.connect)
        else:
            reactor.stop()


class Client(irc.IRCClient):
    """
    An implementation of :class:`twisted.words.protocols.irc.IRCClient` with some overrides
    derived from helga settings (see :ref:`config`). Some methods are overridden
    to provide additional functionality.

    .. attribute:: channels
        :annotation: = set()

        A set containing all of the channels the bot is currently in

    .. attribute:: operators
        :annotation: = set()

        A set containing all of the configured operators (setting :data:`~helga.settings.OPERATORS`)

    .. attribute:: last_message
        :annotation: = dict()

        A channel keyed dictionary containing dictionaries of nick -> message of the last messages
        the bot has seen a user send on a given channel. For instance, if in the channel ``#foo``::

            <sduncan> test

        The contents of this dictionary would be::

            self.last_message['#foo']['sduncan'] = 'test'

    .. attribute:: channel_loggers
        :annotation: = dict()

        A dictionary of known channel loggers, keyed off the channel name
    """

    #: The preferred IRC nick of the bot instance (setting :data:`~helga.settings.NICK`)
    nickname = None

    #: A username should the IRC server require authentication (setting :data:`~helga.settings.SERVER`)
    username = None

    #: A password should the IRC server require authentication (setting :data:`~helga.settings.SERVER`)
    password = None

    #: An integer, in seconds, if IRC messages should be sent at a limit of once per this many seconds.
    #: ``None`` implies no limit. (setting :data:`~helga.settings.RATE_LIMIT`)
    lineRate = None

    #: The URL where the source of the bot is found
    sourceURL = 'http://github.com/shaunduncan/helga'

    #: The assumed encoding of IRC messages
    encoding = 'UTF-8'

    #: A backup nick should the preferred :attr:`nickname` be taken. This defaults to a string in the
    #: form of the preferred nick plus the timestamp when the process was started (i.e. helga_12345)
    erroneousNickFallback = None

    def __init__(self, factory=None):
        self.factory = factory
        self.erroneousNickFallback = '{0}_{1}'.format(settings.NICK, int(time.time()))

        # These are set here to ensure using properly overridden settings
        self.nickname = settings.NICK
        self.username = settings.SERVER.get('USERNAME', None)
        self.password = settings.SERVER.get('PASSWORD', None)
        self.lineRate = getattr(settings, 'RATE_LIMIT', None)

        # Pre-configured helga admins
        self.operators = set(getattr(settings, 'OPERATORS', []))

        # Things to keep track of
        self.channels = set()
        self.last_message = defaultdict(dict)  # Dict of x[channel][nick]
        self.channel_loggers = {}

    def get_channel_logger(self, channel):
        """
        Gets a channel logger, keeping track of previously requested ones.
        (see :ref:`builtin.channel_logging`)

        :param str channel: A channel name
        """
        if channel not in self.channel_loggers:
            self.channel_loggers[channel] = log.get_channel_logger(channel)
        return self.channel_loggers[channel]

    def log_channel_message(self, channel, nick, message):
        """
        Logs one or more messages by a user on a channel using a channel logger.
        If channel logging is not enabled, nothing happens. (see :ref:`builtin.channel_logging`)

        :param str channel: A channel name
        :param str nick: The nick of the user sending an IRC message
        :param str message: The IRC message
        """
        if not settings.CHANNEL_LOGGING:
            return
        chan_logger = self.get_channel_logger(channel)
        chan_logger.info(message, extra={'nick': nick})

    def connectionMade(self):
        logger.info('Connection made to %s', settings.SERVER['HOST'])
        irc.IRCClient.connectionMade(self)

    @encodings.from_unicode_args
    def connectionLost(self, reason):
        logger.info('Connection to %s lost: %s', settings.SERVER['HOST'], reason)
        irc.IRCClient.connectionLost(self, reason)

    def signedOn(self):
        """
        Called when the client has successfully signed on to IRC. Establishes automatically
        joining channels. Sends the ``signon`` signal (see :ref:`plugins.signals`)
        """
        for channel in settings.CHANNELS:
            # If channel is more than one item tuple, second value is password
            if len(channel) > 1:
                self.join(encodings.from_unicode(channel[0]),
                          encodings.from_unicode(channel[1]))
            else:
                self.join(encodings.from_unicode(channel[0]))
        smokesignal.emit('signon', self)

    def joined(self, channel):
        """
        Called when the client successfully joins a new channel. Adds the channel to the known
        channel list and sends the ``join`` signal (see :ref:`plugins.signals`)

        :param str channel: the channel that has been joined
        """
        logger.info('Joined %s', channel)
        self.channels.add(channel)
        smokesignal.emit('join', self, channel)

    def left(self, channel):
        """
        Called when the client successfully leaves a channel. Removes the channel from the known
        channel list and sends the ``left`` signal (see :ref:`plugins.signals`)

        :param str channel: the channel that has been left
        """
        logger.info('Left %s', channel)
        self.channels.discard(channel)
        smokesignal.emit('left', self, channel)

    def parse_nick(self, full_nick):
        """
        Parses a nick from a full IRC user string. For example from ``me!~myuser@localhost``
        would return ``me``.

        :param str full_nick: the full IRC user string of the form ``{nick}!~{user}@{host}``
        :returns: The nick portion of the IRC user string
        """
        return full_nick.split('!')[0]

    def is_public_channel(self, channel):
        """
        Checks if a given channel is public or not. A channel is public if it starts with
        '#' and is not the bot's nickname (which occurs when a private message is received)

        :param str channel: the channel name to check
        """
        return self.nickname != channel and channel.startswith('#')

    @encodings.to_unicode_args
    def privmsg(self, user, channel, message):
        """
        Handler for an IRC message. This method handles logging channel messages (if it occurs
        on a public channel) as well as allowing the plugin manager to send the message to all
        registered plugins. Should the plugin manager yield a response, it will be sent back
        over IRC.

        :param str user: IRC user string of the form ``{nick}!~{user}@{host}``
        :param str channel: the channel from which the message came
        :param str message: the message contents
        """
        user = self.parse_nick(user)
        message = message.strip()

        # Log the incoming message and notify message subscribers
        logger.debug('[<--] %s/%s - %s', channel, user, message)
        is_public = self.is_public_channel(channel)

        # When we get a priv msg, the channel is our current nick, so we need to
        # respond to the user that is talking to us
        if is_public:
            # Only log convos on public channels
            self.log_channel_message(channel, user, message)
        else:
            channel = user

        # Some things should go first
        try:
            channel, user, message = registry.preprocess(self, channel, user, message)
        except (TypeError, ValueError):
            pass

        # if not message.has_response:
        responses = registry.process(self, channel, user, message)

        if responses:
            message = u'\n'.join(responses)
            self.msg(channel, message)

            if is_public:
                self.log_channel_message(channel, self.nickname, message)

        # Update last message
        self.last_message[channel][user] = message

    def alterCollidedNick(self, nickname):
        """
        Called when the both has a nickname collision. This will generate a new nick
        containing the perferred nick and the current timestamp.

        :param str nickname: the nickname that was already taken
        """
        logger.info('Nick %s already taken', nickname)

        parts = nickname.split('_')
        if len(parts) > 1:
            parts = parts[:-1]

        stripped = '_'.join(parts)
        self.nickname = '{0}_{1}'.format(stripped, int(time.time()))

        return self.nickname

    def kickedFrom(self, channel, kicker, message):
        logger.warning('%s kicked bot from %s: %s', kicker, channel, message)
        self.channels.discard(channel)

    @encodings.from_unicode_args
    def msg(self, channel, message):
        """
        Send a message over IRC to the specified channel

        :param channel: The IRC channel to send the message to. A channel not prefixed by a '#'
                        will be sent as a private message to a user with that nick.
        :param message: The message to send
        """
        logger.debug('[-->] %s - %s', channel, message)
        irc.IRCClient.msg(self, channel, message)

    def on_invite(self, inviter, invitee, channel):
        """
        Handler for /INVITE commands. If the invitee is the bot, it will join the requested channel.

        :param str inviter: IRC user string of the form ``{nick}!~{user}@{host}``
        :param str invitee: the nick of the user receiving the invite
        :param str channel: the channel to which invitee has been invited
        """
        nick = self.parse_nick(inviter)
        if invitee == self.nickname:
            logger.info('%s invited %s to %s', nick, invitee, channel)
            self.join(channel)

    def irc_unknown(self, prefix, command, params):
        """
        Handler for any unknown IRC commands. Currently handles /INVITE commands

        :param str prefix: any command prefix, such as the IRC user
        :param str command: the IRC command received
        :param list params: list of parameters for the given command
        """
        if command.lower() == 'invite':
            self.on_invite(prefix, params[0], params[1])

    @encodings.from_unicode_args
    def me(self, channel, message):
        """
        Equivalent to: /me message

        :param channel: The IRC channel to send the message to. A channel not prefixed by a '#'
                        will be sent as a private message to a user with that nick.
        :param message: The message to send
        """
        # A proxy for the WTF-named method `describe`. Basically the same as doing `/me waves`
        irc.IRCClient.describe(self, channel, message)

    def userJoined(self, user, channel):
        """
        Called when a user joins a channel in which the bot resides. Responsible for sending
        the ``user_joined`` signal (see :ref:`plugins.signals`)

        :param str user: IRC user string of the form ``{nick}!~{user}@{host}``
        :param str channel: the channel in which the event occurred
        """
        nick = self.parse_nick(user)
        smokesignal.emit('user_joined', self, nick, channel)

    def userLeft(self, user, channel):
        """
        Called when a user leaves a channel in which the bot resides. Responsible for sending
        the ``user_left`` signal (see :ref:`plugins.signals`)

        :param str user: IRC user string of the form ``{nick}!~{user}@{host}``
        :param str channel: the channel in which the event occurred
        """
        nick = self.parse_nick(user)
        smokesignal.emit('user_left', self, nick, channel)

    @encodings.from_unicode_args
    def join(self, channel, key=None):
        """
        Join a channel, optionally with a passphrase required to join.

        :param str channel: the name of the channel to join
        :param str key: an optional passphrase used to join the given channel
        """
        logger.info("Joining channel %s", channel)
        irc.IRCClient.join(self, channel, key=key)

    @encodings.from_unicode_args
    def leave(self, channel, reason=None):
        """
        Leave a channel, optionally with a reason for leaving

        :param str channel: the name of the channel to leave
        :param str reason: an optional reason for leaving
        """
        logger.info("Leaving channel %s: %s", channel, reason)
        irc.IRCClient.leave(self, channel, reason=reason)
