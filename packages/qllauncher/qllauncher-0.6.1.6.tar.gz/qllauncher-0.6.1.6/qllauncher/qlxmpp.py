"""
QuakeLive Launcher
Copyright (C) 2014  Victor Polevoy <vityatheboss@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = 'Victor Polevoy'


import sleekxmpp
import logging
import time


## Connects to QuakeLive XMPP server and listens it's notifications.
#
class QLXMPP():
    quake_live_xmpp_account_pattern = '%s@xmpp.quakelive.com'

    def __init__(self, username, password, connection_status_handler):
        self._username = QLXMPP.quake_live_xmpp_account_pattern % username
        self._password = password
        self.connection_status_handler = connection_status_handler
        self._is_session_started = None
        self._frontends = []
        self.add_xmpp_frontend(QLXMPPDefaultFrontend())
        self.people_online = []
        self.messages = {}

        self.roster = None

        self._xmpp = sleekxmpp.ClientXMPP(self._username, self._password)
        self._xmpp.add_event_handler('session_start', self._on_session_start)
        self._xmpp.add_event_handler('session_end', self._on_session_end)
        self._xmpp.add_event_handler('message', self._on_message_received)
        for event in ['got_online', 'got_offline', 'changed_status', 'on_auth_fail']:
            self._xmpp.add_event_handler(event, self._notify_frontends_with_event)

        self._xmpp.register_plugin('xep_0030')
        self._xmpp.register_plugin('xep_0199')

    ## @return username of current xmpp account that has been used to log in.
    def get_username(self):
        return self._username

    def _on_session_start(self, event):
        logging.debug('Session started')
        self._is_session_started = True

        if self.connection_status_handler:
            self.connection_status_handler(self._is_session_started)

        self._xmpp.send_presence()
        self._xmpp.get_roster()
        logging.debug('Roster is: %s' % str(self._xmpp.roster))

    def _on_session_end(self, event):
        logging.debug('Session ended')

        self._is_session_started = False

        if self.connection_status_handler:
            self.connection_status_handler(self._is_session_started)

    def _on_message_received(self, event):
        logging.debug('Received message: %s' % event)
        self._notify_frontends_with_event(event)

    ## Adds xmpp frontend to listen XMPP notifications.
    # @param frontend Derived class of QLXMPPFrontend
    # @see QLXMPPFrontend
    def add_xmpp_frontend(self, frontend):
        if frontend and frontend not in self._frontends:
            self._frontends.append(frontend)
            frontend._xmpp_connection = self

    def _notify_frontends_with_event(self, event):
        for frontend in self._frontends:
            frontend.event_received(event)

    ## Sends XMPP chat message.
    # @param to Message recipient
    # @param message Message body
    def send_message(self, to, message):
        sender = self._username + '/quakelive'
        self._xmpp.send_message(mto=to, mbody=message, mfrom=sender, mtype='chat')
        self.append_message(to, sender, message)
        logging.debug('A message to %s has been sent: %s' % (to, message))

    ## Append message to the list of messages for the user.
    # @param companion Message recipient
    # @param sender Message sender
    # @param message Message body
    def append_message(self, companion, sender, message):
        if companion not in self.messages.keys():
            self.messages[companion] = {}

        msg_time = time.strftime('%H:%M:%S')
        if msg_time not in self.messages[companion].keys():
            self.messages[companion][msg_time] = []
        self.messages[companion][msg_time].append({'from': sender, 'message': message})

    ## Converts sleekxmpp.JID -object to a dictionary
    # @return Dictionary object of jabber account
    @staticmethod
    def jid_to_dict(jid):
        return {
            'user': jid.user,
            'account': jid.bare,
            'jid': jid.jid,
            'section': 'People'
        }

    ## Connects to QuakeLive XMPP server
    def connect_to_quake_live_server(self, wait_until_session_change=False):
        logging.debug('Trying to connect to XMPP with (username="%s") and (password="%s")' %
                      (self._username, self._password))

        if self._xmpp.connect(reattempt=False):
            self._xmpp.process()

            if wait_until_session_change:
                while self._is_session_started is None:
                    time.sleep(1)
        else:
            logging.error('Error while connecting to XMPP server.')

        return self._is_session_started

    def disconnect(self):
        self._xmpp.disconnect()


class QLXMPPFrontend():
    def __init__(self):
        self._xmpp_connection = None

    ## Method being invoked from QLXMPP object on any received event.
    def event_received(self, event):
        raise NotImplementedError('Not implemented method of QLXMPP frontend')


class QLXMPPDefaultFrontend(QLXMPPFrontend):
    def __init__(self):
        QLXMPPFrontend.__init__(self)

    def event_received(self, event):
        if event.name == 'presence':
            self.presence_received(event)
        elif event.name == 'message':
            self.messsage_received(event)
        else:
            self.unknown_event_received(event)

    def messsage_received(self, event):
        logging.debug('Message received: %s' % str(event))

        self._xmpp_connection.append_message(event.values['from'].jid, event.values['from'].jid, event.values['body'])

    def presence_received(self, event):
        if event.values['from'].bare != self._xmpp_connection.get_username():
            if event.values['from'].resource:
                user = QLXMPP.jid_to_dict(event.values['from'])

                if event.values['status']:
                    user['current_server'] = eval(event.values['status'])
                else:
                    user['current_server'] = None

                user['has_unread_messages'] = False

                if event.values['type'] == 'available':
                    added = False

                    for u in self._xmpp_connection.people_online:
                        if u['user'] == user['user']:
                            u['current_server'] = user['current_server']

                            added = True
                    if not added:
                        self._xmpp_connection.people_online.append(user)
                else:
                    if user in self._xmpp_connection.people_online:
                        self._xmpp_connection.people_online.remove(user)
        elif event.values['type'] == 'unavailable':
            self._xmpp_connection._xmpp.send_presence(pshow='available',
                                                      ptype='available',
                                                      pfrom=self._xmpp_connection.get_username() + '/quakelive',
                                                      pstatus=event.values['status'],
                                                      ppriority=0)

        logging.debug('Presence received: %s' % str(event))

    def unknown_event_received(self, event):
        logging.debug('Unknown event received: %s' % str(event))

    # def get_messages_from(self, user):
    #     for msg in self.messages:
    #         if msg