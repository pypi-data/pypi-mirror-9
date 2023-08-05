# -*- coding: utf-8 -*-
# server.py
# Copyright (C) 2014 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Leap IMAP4 Server Implementation.
"""
from copy import copy

from twisted import cred
from twisted.internet.defer import maybeDeferred
from twisted.mail import imap4
from twisted.python import log

from leap.common import events as leap_events
from leap.common.check import leap_assert, leap_assert_type
from leap.common.events.events_pb2 import IMAP_CLIENT_LOGIN
from leap.soledad.client import Soledad

# imports for LITERAL+ patch
from twisted.internet import defer, interfaces
from twisted.mail.imap4 import IllegalClientResponse
from twisted.mail.imap4 import LiteralString, LiteralFile


class LeapIMAPServer(imap4.IMAP4Server):
    """
    An IMAP4 Server with mailboxes backed by soledad
    """
    def __init__(self, *args, **kwargs):
        # pop extraneous arguments
        soledad = kwargs.pop('soledad', None)
        uuid = kwargs.pop('uuid', None)
        userid = kwargs.pop('userid', None)

        leap_assert(soledad, "need a soledad instance")
        leap_assert_type(soledad, Soledad)
        leap_assert(uuid, "need a user in the initialization")

        self._userid = userid

        # initialize imap server!
        imap4.IMAP4Server.__init__(self, *args, **kwargs)

        # we should initialize the account here,
        # but we move it to the factory so we can
        # populate the test account properly (and only once
        # per session)

        from twisted.internet import reactor
        self.reactor = reactor

    def lineReceived(self, line):
        """
        Attempt to parse a single line from the server.

        :param line: the line from the server, without the line delimiter.
        :type line: str
        """
        if self.theAccount.closed is True and self.state != "unauth":
            log.msg("Closing the session. State: unauth")
            self.state = "unauth"

        if "login" in line.lower():
            # avoid to log the pass, even though we are using a dummy auth
            # by now.
            msg = line[:7] + " [...]"
        else:
            msg = copy(line)
        log.msg('rcv (%s): %s' % (self.state, msg))
        imap4.IMAP4Server.lineReceived(self, line)

    def authenticateLogin(self, username, password):
        """
        Lookup the account with the given parameters, and deny
        the improper combinations.

        :param username: the username that is attempting authentication.
        :type username: str
        :param password: the password to authenticate with.
        :type password: str
        """
        # XXX this should use portal:
        # return portal.login(cred.credentials.UsernamePassword(user, pass)
        if username != self._userid:
            # bad username, reject.
            raise cred.error.UnauthorizedLogin()
        # any dummy password is allowed so far. use realm instead!
        leap_events.signal(IMAP_CLIENT_LOGIN, "1")
        return imap4.IAccount, self.theAccount, lambda: None

    def do_FETCH(self, tag, messages, query, uid=0):
        """
        Overwritten fetch dispatcher to use the fast fetch_flags
        method
        """
        if not query:
            self.sendPositiveResponse(tag, 'FETCH complete')
            return

        cbFetch = self._IMAP4Server__cbFetch
        ebFetch = self._IMAP4Server__ebFetch

        if len(query) == 1 and str(query[0]) == "flags":
            self._oldTimeout = self.setTimeout(None)
            # no need to call iter, we get a generator
            maybeDeferred(
                self.mbox.fetch_flags, messages, uid=uid
            ).addCallback(
                cbFetch, tag, query, uid
            ).addErrback(ebFetch, tag)

        elif len(query) == 1 and str(query[0]) == "rfc822.header":
            self._oldTimeout = self.setTimeout(None)
            # no need to call iter, we get a generator
            maybeDeferred(
                self.mbox.fetch_headers, messages, uid=uid
            ).addCallback(
                cbFetch, tag, query, uid
            ).addErrback(ebFetch, tag)
        else:
            self._oldTimeout = self.setTimeout(None)
            # no need to call iter, we get a generator
            maybeDeferred(
                self.mbox.fetch, messages, uid=uid
            ).addCallback(
                cbFetch, tag, query, uid
            ).addErrback(
                ebFetch, tag)

    select_FETCH = (do_FETCH, imap4.IMAP4Server.arg_seqset,
                    imap4.IMAP4Server.arg_fetchatt)

    def notifyNew(self, ignored=None):
        """
        Notify new messages to listeners.
        """
        self.reactor.callFromThread(self.mbox.notify_new)

    def _cbSelectWork(self, mbox, cmdName, tag):
        """
        Callback for selectWork, patched to avoid conformance errors due to
        incomplete UIDVALIDITY line.
        """
        if mbox is None:
            self.sendNegativeResponse(tag, 'No such mailbox')
            return
        if '\\noselect' in [s.lower() for s in mbox.getFlags()]:
            self.sendNegativeResponse(tag, 'Mailbox cannot be selected')
            return

        flags = mbox.getFlags()
        self.sendUntaggedResponse(str(mbox.getMessageCount()) + ' EXISTS')
        self.sendUntaggedResponse(str(mbox.getRecentCount()) + ' RECENT')
        self.sendUntaggedResponse('FLAGS (%s)' % ' '.join(flags))

        # Patched -------------------------------------------------------
        # imaptest was complaining about the incomplete line, we're adding
        # "UIDs valid" here.
        self.sendPositiveResponse(
            None, '[UIDVALIDITY %d] UIDs valid' % mbox.getUIDValidity())
        # ----------------------------------------------------------------

        s = mbox.isWriteable() and 'READ-WRITE' or 'READ-ONLY'
        mbox.addListener(self)
        self.sendPositiveResponse(tag, '[%s] %s successful' % (s, cmdName))
        self.state = 'select'
        self.mbox = mbox

    def checkpoint(self):
        """
        Called when the client issues a CHECK command.

        This should perform any checkpoint operations required by the server.
        It may be a long running operation, but may not block.  If it returns
        a deferred, the client will only be informed of success (or failure)
        when the deferred's callback (or errback) is invoked.
        """
        # TODO return the output of _memstore.is_writing
        # XXX and that should return a deferred!
        return None

    #############################################################
    #
    # Twisted imap4 patch to support LITERAL+ extension
    # TODO send this patch upstream asap!
    #
    #############################################################

    def capabilities(self):
        cap = {'AUTH': self.challengers.keys()}
        if self.ctx and self.canStartTLS:
            t = self.transport
            ti = interfaces.ISSLTransport
            if not self.startedTLS and ti(t, None) is None:
                cap['LOGINDISABLED'] = None
                cap['STARTTLS'] = None
        cap['NAMESPACE'] = None
        cap['IDLE'] = None
        # patched ############
        cap['LITERAL+'] = None
        ######################
        return cap

    def _stringLiteral(self, size, literal_plus=False):
        if size > self._literalStringLimit:
            raise IllegalClientResponse(
                "Literal too long! I accept at most %d octets" %
                (self._literalStringLimit,))
        d = defer.Deferred()
        self.parseState = 'pending'
        self._pendingLiteral = LiteralString(size, d)
        # Patched ###########################################################
        if not literal_plus:
            self.sendContinuationRequest('Ready for %d octets of text' % size)
        #####################################################################
        self.setRawMode()
        return d

    def _fileLiteral(self, size, literal_plus=False):
        d = defer.Deferred()
        self.parseState = 'pending'
        self._pendingLiteral = LiteralFile(size, d)
        if not literal_plus:
            self.sendContinuationRequest('Ready for %d octets of data' % size)
        self.setRawMode()
        return d

    def arg_astring(self, line):
        """
        Parse an astring from the line, return (arg, rest), possibly
        via a deferred (to handle literals)
        """
        line = line.strip()
        if not line:
            raise IllegalClientResponse("Missing argument")
        d = None
        arg, rest = None, None
        if line[0] == '"':
            try:
                spam, arg, rest = line.split('"', 2)
                rest = rest[1:]  # Strip space
            except ValueError:
                raise IllegalClientResponse("Unmatched quotes")
        elif line[0] == '{':
            # literal
            if line[-1] != '}':
                raise IllegalClientResponse("Malformed literal")

            # Patched ################
            if line[-2] == "+":
                literalPlus = True
                size_end = -2
            else:
                literalPlus = False
                size_end = -1

            try:
                size = int(line[1:size_end])
            except ValueError:
                raise IllegalClientResponse(
                    "Bad literal size: " + line[1:size_end])
            d = self._stringLiteral(size, literalPlus)
            ##########################
        else:
            arg = line.split(' ', 1)
            if len(arg) == 1:
                arg.append('')
            arg, rest = arg
        return d or (arg, rest)

    def arg_literal(self, line):
        """
        Parse a literal from the line
        """
        if not line:
            raise IllegalClientResponse("Missing argument")

        if line[0] != '{':
            raise IllegalClientResponse("Missing literal")

        if line[-1] != '}':
            raise IllegalClientResponse("Malformed literal")

        # Patched ##################
        if line[-2] == "+":
            literalPlus = True
            size_end = -2
        else:
            literalPlus = False
            size_end = -1

        try:
            size = int(line[1:size_end])
        except ValueError:
            raise IllegalClientResponse(
                "Bad literal size: " + line[1:size_end])

        return self._fileLiteral(size, literalPlus)
        #############################

    # Need to override the command table after patching
    # arg_astring and arg_literal

    do_LOGIN = imap4.IMAP4Server.do_LOGIN
    do_CREATE = imap4.IMAP4Server.do_CREATE
    do_DELETE = imap4.IMAP4Server.do_DELETE
    do_RENAME = imap4.IMAP4Server.do_RENAME
    do_SUBSCRIBE = imap4.IMAP4Server.do_SUBSCRIBE
    do_UNSUBSCRIBE = imap4.IMAP4Server.do_UNSUBSCRIBE
    do_STATUS = imap4.IMAP4Server.do_STATUS
    do_APPEND = imap4.IMAP4Server.do_APPEND
    do_COPY = imap4.IMAP4Server.do_COPY

    _selectWork = imap4.IMAP4Server._selectWork
    _listWork = imap4.IMAP4Server._listWork
    arg_plist = imap4.IMAP4Server.arg_plist
    arg_seqset = imap4.IMAP4Server.arg_seqset
    opt_plist = imap4.IMAP4Server.opt_plist
    opt_datetime = imap4.IMAP4Server.opt_datetime

    unauth_LOGIN = (do_LOGIN, arg_astring, arg_astring)

    auth_SELECT = (_selectWork, arg_astring, 1, 'SELECT')
    select_SELECT = auth_SELECT

    auth_CREATE = (do_CREATE, arg_astring)
    select_CREATE = auth_CREATE

    auth_EXAMINE = (_selectWork, arg_astring, 0, 'EXAMINE')
    select_EXAMINE = auth_EXAMINE

    auth_DELETE = (do_DELETE, arg_astring)
    select_DELETE = auth_DELETE

    auth_RENAME = (do_RENAME, arg_astring, arg_astring)
    select_RENAME = auth_RENAME

    auth_SUBSCRIBE = (do_SUBSCRIBE, arg_astring)
    select_SUBSCRIBE = auth_SUBSCRIBE

    auth_UNSUBSCRIBE = (do_UNSUBSCRIBE, arg_astring)
    select_UNSUBSCRIBE = auth_UNSUBSCRIBE

    auth_LIST = (_listWork, arg_astring, arg_astring, 0, 'LIST')
    select_LIST = auth_LIST

    auth_LSUB = (_listWork, arg_astring, arg_astring, 1, 'LSUB')
    select_LSUB = auth_LSUB

    auth_STATUS = (do_STATUS, arg_astring, arg_plist)
    select_STATUS = auth_STATUS

    auth_APPEND = (do_APPEND, arg_astring, opt_plist, opt_datetime,
                   arg_literal)
    select_APPEND = auth_APPEND

    select_COPY = (do_COPY, arg_seqset, arg_astring)


    #############################################################
    # END of Twisted imap4 patch to support LITERAL+ extension
    #############################################################
