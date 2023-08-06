# Copyright (c) 2014 Tobias Marquardt
#
# Distributed under terms of the (2-clause) BSD license.

"""
This module provides functions for parsing of irc messages.
This is not an implementation of a complete parser but just
functions that parse specific (parts of) irc messages and extract some
information for further processing. Parsing errors might be raised on invalid
input, but an accepted input does not automatically mean that it conforms to
the irc message grammar (as described in RFC 2812).
"""

__all__ = []

from fredirc.errors import ParserError
from fredirc.messages import ChannelMode


def parse(message):
    """ Parse a message and extract prefix, command and paramaters.

    Relevant part of the protocol's grammar:
       message    =  [ ":" prefix SPACE ] command [ params ] crlf
       command    =  1*letter / 3digit
       params     =  *14( SPACE middle ) [ SPACE ":" trailing ]
                  =/ 14( SPACE middle ) [ SPACE [ ":" ] trailing ]
    Prefix and parameters may be None. On the prefix and so called 'trailing'
    parameter (i.e. parameter with possible whitespaces) the leading colon is
    removed.

    Args:
        message (str): Raw irc message (without the CRLF)
    Retval:
        3-element tuple: two strings (prefix and command) and a tuple of
        strings (params)
    """
    prefix = None
    params = None
    # Prefix
    if message.startswith(':'):
        try:
            prefix, message = message.split(None, 1)
        except ValueError:
            raise ParserError('Malformed message: {}'.format(message))
        prefix = prefix[1:]
    # Command
    try:
        tmp_split = message.split(None, 1)
    except ValueError:
        raise ParserError('Malformed message: {}'.format(message))
    command = tmp_split[0]
    # Parameters
    if len(tmp_split) == 2:
        param_split = tmp_split[1].split(':', 1)
        params = param_split[0].split()
        if len(param_split) == 2:
            params.append(param_split[1])
    return prefix, command, params


def parse_user_prefix(prefix):
    """
    Parses:
        prefix = nickname [ [ "!" user ] "@" host ]
    Retval:
        triple (nick, user, host), user and host might be None
    """
    user = None
    host = None
    nick = prefix
    host_split = prefix.split('@', 1)
    if len(host_split) == 2:
        nick = host_split[0]
        host = host_split[1]
        user_split = nick.split('!', 1)
        if len(user_split) == 2:
            nick = user_split[0]
            user = user_split[1]
    return nick, user, host


def parse_message_target(msg_target):
    """ Parse a message target.

    Parses:
      msgtarget  =  msgto *( "," msgto )
      msgto      =  channel / ( user [ "%" host ] "@" servername )
      msgto      =/ ( user "%" host ) / targetmask
      msgto      =/ nickname / ( nickname "!" user "@" host )
      channel    =  ( "#" / "+" / ( "!" channelid ) / "&" ) chanstring
                    [ ":" chanstring ]
    Retval:
        Tuple of :py:class:`.MessageTarget`s, where each MessageTarget
        represents one 'msgto' from the grammar rule
    """
    targets = list()
    targets_split = msg_target.split(',')
    for msgto in targets_split:
        # TODO does not completely implement the specs
        #      (no channel ids and collon delimiters)
        if msgto.startswith('#') or \
           msgto.startswith('+') or \
           msgto.startswith('&'):
            # We want channel names to always be lower-case in fredirc!
            mt = MessageTarget(channel=msgto.lower())
        elif '@' in msgto:
            user_split = msgto.split('@', 1)
            if '!' in user_split[0]:
                nick_split = user_split[0].split('!', 1)
                mt = MessageTarget(nick=nick_split[0], user=nick_split[1],
                                   host=user_split[1])
            else:
                if '%' in user_split[0]:
                    host_split = user_split[0].split('%', 1)
                    mt = MessageTarget(user=host_split[0], host=host_split[1],
                                       server=user_split[1])
                else:
                    mt = MessageTarget(user=user_split[0],
                                       server=user_split[1])
        elif '%' in msgto:
            user_split = msgto.split('%', 1)
            mt = MessageTarget(user=user_split[0], host=user_split[1])
        elif (msgto.startswith('$') or msgto.startswith('#')) and '.' in msgto:
            mt = MessageTarget(target_mask=msgto)
        else:
            mt = MessageTarget(nick=msgto)
        targets.append(mt)
    return tuple(targets)


def parse_channel_mode_params(params):
    """ Parse parameters of a channel mode message.

    The channel name must not be included in the parameter list!
    .. warning::
        This is incomplete! So far we only parse those modes that are
        handled by FredIRC.

    Parses: *( ( "-" / "+" ) *<modes> *<modeparams> )

    Retval:
        tuple of ChannelModeChange
    """
    if not params[0].startswith('+') and not params[0].startswith('-'):
        raise ParserError(str(params))  #TODO ParserError expects the whole mesasge
    mode_changes = []

    for param in params:
        added = None
        if param.startswith('+'):
            added = True
        elif param.startswith('-'):
            added = False

        if added is None:
            # param contains <modeparams> for the previous modeChange
            if len(mode_changes):
                if not mode_changes[-1].params:
                    mode_changes[-1].params = []
                mode_changes[-1].params.append(param)
        else:   # param contains <modes>
            # Easy so far, as we are only looking for a 'o' or 'v' at the end of
            # the modes (they must be at the end, because they expect a
            # parameter)
            mode = param[-1:]
            if mode == ChannelMode.OPERATOR or \
               mode == ChannelMode.VOICE:
                mode_changes.append(ChannelModeChange(added, mode))

    return tuple(mode_changes)


class ChannelModeChange(object):
    """ Object that contains information about a changed channel mode.

    Note: Does not contain the channel name itself, but only the parameters
    of the mode-message.

    Args:
        added (bool): True, if the mode was added. False, otherwise.
        mode (str): the mode
        params (tuple of str): Parameters of this mode-change (e.g. target)
    """

    def __init__(self, added, mode, params=None):
        self.added = added
        self.mode = mode
        self.params = params


class MessageTarget(object):
    """ Represents a target of an IRC message.

    Corresponds to the non-terminal 'msgto' in IRC's grammar.
    """

    def __init__(self, channel=None, nick=None, user=None, host=None,
                 server=None, target_mask=None):
        self.channel = channel
        self.nick = nick
        self.user = user
        self.host = host
        self.server = server
        self.target_mask = target_mask
