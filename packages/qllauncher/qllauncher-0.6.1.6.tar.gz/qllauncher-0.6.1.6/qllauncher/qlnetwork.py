"""
QuakeLive Launcher
Copyright (C) 2014  Victor Polevoy (vityatheboss@gmail.com)

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

import urllib.request
import urllib.parse
import http.cookiejar
import http.cookies
import requests
import json
import time
import threading
import logging
import re
import base64

from qllauncher.qlxmpp import QLXMPP
from qllauncher.helpers.singleton import Singleton


## Encapsulates interaction between client and quakelive network.
# Connects, disconnects, sends and retrieves information.
class QLNetwork(metaclass=Singleton):
    _quake_live_join_link_pattern = 'http://www.quakelive.com/#!join/'
    _quake_live_cdn_flags_pattern = 'http://cdn.quakelive.com/web/1/images/flags/%s.gif'

    # locations are filled dynamically by calling self._fill_locations() and only after logging in
    locations = {
        'any': 'In Your Vicinity',
        'ALL': 'All Locations',
    }

    # key - location id, value = country abbr
    # example: 18: "ru"
    location_flags = {

    }

    game_types_unranked = {
        8: 'InstaFFA',
        21: 'Insta1FCTF',
        23: 'InstaA&D',
        14: 'InstaCA',
        9: 'InstaCTF',
        20: 'InstaDOM',
        10: 'InstaFreeze',
        22: 'InstaHAR',
        24: 'InstaRR',
        11: 'InstaTDM',
    }

    game_types = {
        'any': 'Any Game Type',
        0: "Free For All",
        1: "Duel",
        2: "Race",
        3: "Team DeathMatch",
        4: "Clan Arena",
        5: "Capture The Flag",
        6: "1-Flag CTF",
        8: "Harvester",
        9: "Freeze Tag",
        10: "Domination",
        11: "Attack & Defend",
        12: "Red Rover"
    }

    rule_sets = {
        1: 'Classic',
        2: 'Turbo',
        3: 'Default'
    }

    class Status():
        DISCONNECTED = 0
        CONNECTED = 1
        CONNECTING = 2

    def __init__(self, email=None, password=None):
        if email:
            self.email = email
        if password:
            self.password = password

        self.listeners = []
        self.ql_session = None
        self.gt_pass = None
        self.gt_user = None
        self.ql_user_info = None
        self.ql_map_db = None
        self._xmpp = None
        self._cookie_jar = None
        self._connect_lock = threading.Lock()

    def is_connected(self):
        if self.ql_session:
            return True

        return False

    def connect(self, email=None, password=None):
        with self._connect_lock:
            if not self.is_connected():
                if email and password:
                    self.email = email
                    self.password = password

                if self.email and self.password:
                    self._notify_listeners(QLNetwork.Status.CONNECTING)
                    self._cookie_jar = http.cookiejar.CookieJar()
                    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self._cookie_jar))
                    data = urllib.parse.urlencode({'submit': '', 'email': self.email, 'pass': self.password})
                    data = data.encode('utf-8')
                    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0')]
                    opener.open('https://secure.quakelive.com/user/login', data)

                    self.ql_session = self._cookie_jar._cookies['.quakelive.com']['/']['quakelive_sess'].value

                    self.ql_user_info = self.get_ql_user_info()
                    self.gt_user = self.ql_user_info['USERNAME']
                    self.gt_pass = self.ql_user_info['XAID']
                    self.ql_map_db = self.ql_user_info['MAPDB']

                    if not self._xmpp_connect():
                        self.disconnect()
                        msg = 'Failed to connect to QuakeLive network (XMPP Authentication failed).'
                        logging.error(msg)
                        raise KeyError(msg)

                    self._fill_locations()
                    self._notify_listeners(QLNetwork.Status.CONNECTED)
                else:
                    raise KeyError('No email and/or password provided')

    def _xmpp_connect(self):
        self._xmpp = QLXMPP(username=self.gt_user,
                            password=self.gt_pass,
                            connection_status_handler=None)

        return self._xmpp.connect_to_quake_live_server(True)

    def disconnect(self):
        requests.get('http://www.quakelive.com/#!logoff', cookies=self._cookie_jar)

        if self._xmpp:
            self._xmpp.disconnect()
            self._xmpp = None

        self.ql_user_info = None
        self.gt_pass = None
        self.ql_session = None
        self._notify_listeners(QLNetwork.Status.DISCONNECTED)

    def reconnect(self):
        logging.info('Reconnecting')
        self.disconnect()
        self.connect()

    def _notify_listeners(self, status):
        for listener in self.listeners:
            listener.network_status_changed(status)

    ## @return dict object with a list of receives invites.
    def retrieve_invites(self):
        response = requests.get('http://www.quakelive.com/startamatch/revokeinvite', cookies=self._cookie_jar)

        response = response.json()

        if response['ECODE'] == -1:
            return None

        return response

    ## Send invite to a <nick> to join a server with server id == server_id
    # @param nick Nickname of a player to receive invite
    # @param server_id Public id of the server you want to let player to join
    def send_invite(self, nick, server_id):
        response = requests.post('http://www.quakelive.com/request/invite',
                                 data={'user': nick, 'server_id': server_id},
                                 cookies=self._cookie_jar)

        response = response.json()

        if response['ECODE'] == -1:
            return None

        return response

    ## @return dict object with a list of sent invites.
    def my_invites_to_server(self, server_id):
        response = requests.get('http://www.quakelive.com/startamatch/invites/%s' % str(server_id),
                                cookies=self._cookie_jar)

        response = response.json()

        if response['ECODE'] == -1:
            return None

        return response

    ## Adds a listener to xmpp notifications (chat, presence, etc)
    # @param frontend Listener object. Must be derived of QLXMPPFrontend class
    # @see QLXMPPFrontend
    def add_xmpp_frontend(self, frontend):
        if self._xmpp:
            self._xmpp.add_xmpp_frontend(frontend)

    ## Fills location variable from QuakeLive network information (dynamically from quakelive.com/load)
    def _fill_locations(self):
        if self.ql_user_info:
            for location in self.ql_user_info['LOCATIONS']:
                if location['pub'] != 0:
                    QLNetwork.locations[location['location_id']] = '%s - %s' % (location['display_country'],
                                                                                location['display_city'])

                    QLNetwork._parse_and_add_location_flag(location['display_country_abbr'], location['location_id'])

    ## Fills location_flags with flag images.
    @staticmethod
    def _parse_and_add_location_flag(country_abbr, location_id):
        flag = QLNetwork._parse_flag(country_abbr)
        QLNetwork.location_flags[location_id] = QLNetwork._quake_live_cdn_flags_pattern % flag

    # TODO rewrite as map
    @staticmethod
    def _parse_flag(country_abbr):
        if country_abbr.lower() == 'usa':
            return 'us'
        elif country_abbr.lower() == 'aus':
            return 'au'
        elif country_abbr.lower() == 'nld':
            return 'nl'
        elif country_abbr.lower() == 'deu':
            return 'de'
        elif country_abbr.lower() == 'gbr':
            return 'gb'
        elif country_abbr.lower() == 'fra':
            return 'fr'
        elif country_abbr.lower() == 'can':
            return 'ca'
        elif country_abbr.lower() == 'jpn':
            return 'jp'
        elif country_abbr.lower() == 'esp':
            return 'es'
        elif country_abbr.lower() == 'swe':
            return 'se'
        elif country_abbr.lower() == 'pol':
            return 'pl'
        elif country_abbr.lower() == 'chn':
            return 'cn'
        elif country_abbr.lower() == 'rom':
            return 'ro'
        elif country_abbr.lower() == 'chl':
            return 'cl'
        elif country_abbr.lower() == 'isl':
            return 'is'
        elif country_abbr.lower() == 'rus':
            return 'ru'
        elif country_abbr.lower() == 'sgp':
            return 'sg'
        elif country_abbr.lower() == 'zaf':
            return 'za'
        elif country_abbr.lower() == 'srb':
            return 'rs'
        elif country_abbr.lower() == 'bgr':
            return 'bg'
        elif country_abbr.lower() == 'kor':
            return 'kr'
        elif country_abbr.lower() == 'ita':
            return 'it'
        elif country_abbr.lower() == 'ukr':
            return 'ua'
        elif country_abbr.lower() == 'nor':
            return 'no'
        elif country_abbr.lower() == 'bra':
            return 'br'
        elif country_abbr.lower() == 'tur':
            return 'tr'
        elif country_abbr.lower() == 'nzl':
            return 'nz'
        elif country_abbr.lower() == 'arg':
            return 'ar'
        else:
            return None

    ## Gets server information from a custom string.
    # @return Dictionary with server parameters.
    def get_server_info(self, ql_server_string):
        server_info = None

        if ql_server_string:
            # getting right element of uri (if it is really uri)
            string = ql_server_string

            try:
                string = ql_server_string.rsplit('/', 1)[1]
            except IndexError:
                pass

            # parsing string like: http://www.quakelive.com/#!join/e7173554-8d35-44b4-8297-e85a59ef1b7c
            if re.match('(\w+)-(\w+)-(\w+)-(\w+)-(\w+)', string):
                server_id = self._get_server_info_by_long_server_string(string)['player_id']
                server_info = self._get_server_info_by_public_server_id(server_id)
            # parsing string like: http://www.quakelive.com/#!join/123456
            elif re.match('(\d{6})', string):
                server_info = self._get_server_info_by_public_server_id(string)

        return server_info

    ## Gets real connect string (/connect <ip address>).
    # @return Connect string to be used while launching the game if success, None otherwise.
    def get_connect_string(self, server_string):
        try:
            server_ip = self.get_server_info(server_string)
            if server_ip:
                server_ip = server_ip['host_address']
        except IndexError:
            server_ip = None

        if server_ip:
            return '+connect %s' % server_ip
        # parsing IP like: 85.21.90.90.27060
        elif re.match('(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3}):(\d{3,5})', server_string):
            port = int(server_string.rsplit(':', 1)[1])

            if 27000 <= port <= 28500:
                return '+connect %s' % server_string
        # parsing string like: /connect 91.198.152.137:27028; password ctf
        elif re.match('(\/?)connect (\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3}):(\d{3,5})(\s*);(\s*)password (.*)',
                      server_string):
            string = server_string.replace('/', '')
            string = string.replace('connect', '+connect')
            string = string.replace('password', '+password')
            string = string.split(';')
            string = '%s %s' % (string[1], string[0])

            return string

    ## Gets quakelive user information (not profile but xmpp connection information, config file, etc)
    # @return Dictionary with user parameters.
    def get_ql_user_info(self, connect=False):
        if connect and not self.is_connected():
            self.connect()
            return self.get_ql_user_info(connect)

        if not self.ql_user_info:
            response = requests.get('http://www.quakelive.com/user/load', cookies=self._cookie_jar)
            self.ql_user_info = response.json()

        return self.ql_user_info

    def _get_server_info_by_long_server_string(self, server_string):
        response = requests.get('http://www.quakelive.com/request/rsvp?inv_code=%s' % server_string,
                                cookies=self._cookie_jar)

        _json = response.json()

        return _json

    @staticmethod
    def _get_server_info_by_public_server_id(server_id):
        response = requests.get('http://www.quakelive.com/browser/details?ids=%s' % server_id)

        _json = response.json()

        if not _json or _json[0]['ECODE'] != 0:
            return None
        else:
            return response.json()[0]

    ## Gets filtered server list.
    # @return List of dictionary objects with server parameters.
    def get_server_list(self, filter):
        encoded_filter = base64.urlsafe_b64encode(bytes(json.dumps(filter), 'utf-8')).decode()

        response = requests.get('http://www.quakelive.com/browser/list?filter=%s' % encoded_filter,
                                cookies=self._cookie_jar)

        return response.json()

    ## Spawns a server with custom settings
    # @param server_settings Dictionary object which has spawn server settings as items.
    # @return List of links by which users can join the spawned server.
    # @see get_packed_server_settings
    def spawn_server_with_settings(self, server_settings, connect=False):
        if connect and not self.is_connected():
            self.connect()
            self.spawn_server_with_settings(server_settings, connect)

        url = 'http://www.quakelive.com/startamatch/start'

        response = requests.post(url, data={'settings': json.dumps(server_settings)}, cookies=self._cookie_jar)
        json_answer = response.json()

        if json_answer['ECODE'] == 0:
            token = json_answer['TOKEN']

            while True:
                response = requests.get('http://www.quakelive.com/startamatch/status', params={'token': token},
                                        cookies=self._cookie_jar)

                if response.json()['ECODE'] == 0:
                    links = {
                        'public_id': response.json()['SERVER_INFO']['SERVER_ID'],
                        'invitation_code': response.json()['SERVER_INFO']['INVITATION_CODE'],
                        'ip': '%s:%s' % (response.json()['SERVER_INFO']['IP'], response.json()['SERVER_INFO']['PORT'])
                    }

                    return links
                elif response.json()['ECODE'] == 2:
                    time.sleep(3)
                else:
                    raise KeyError(response.json()['MSG'])
        else:
            raise KeyError(json_answer['MSG'])

    ## Gets a list of spawned servers with owner == current user logged in.
    # @return List of servers
    def get_spawned_servers_list(self, connect=False):
        if connect and not self.is_connected():
            self.connect()
            return self.get_spawned_servers_list(connect)

        response = requests.get('http://www.quakelive.com/request/myserver', cookies=self._cookie_jar)

        try:
            return response.json()['servers']
        except KeyError:
            return None

    ## Sends server stop signal
    # @param server_public_id Public id of the server which is gonna be stopped
    def send_stop_server_signal(self, server_public_id):
        requests.post('http://www.quakelive.com/request/stopserver',
                      data={'server_id': server_public_id},
                      cookies=self._cookie_jar)

        return True

    ## Sends server stop signal and wait (by using time.sleep) until it really stop (by checking it's existence)
    # @return List of servers.
    def send_stop_server_and_wait_until_it_really_stop(self, server_public_id):
        self.send_stop_server_signal(server_public_id)

        while True:
            servers = self.get_spawned_servers_list(True)

            server_still_running = False

            for server in servers:
                if server['public_id'] == server_public_id:
                    server_still_running = True
                    break

            if server_still_running:
                time.sleep(3)
            else:
                break

    ## Packs server settings (which are method parameters) into a dict-object which may be sent by spawn_server_with_settings
    # @return Dictionary object.
    @staticmethod
    def get_packed_server_settings(location, game_type, maps, password="", hostname="", rule_set=0, invites=""):
        maps = [x.strip() for x in maps]
        invites_map = []

        if invites:
            invites_map = [x.strip() for x in invites]

        cvars = {
            "g_gametype": game_type,
            "g_password": password,
            "sv_hostname": hostname,
            "web_location": location
        }

        if rule_set and rule_set > 0:
            cvars["ruleset"] = rule_set

        server_settings = {
            "invites": invites_map,
            "maps": maps,
            "cvars": cvars
        }

        return server_settings

    ## Parses a player count from server parameter object.
    # @return Tuple with player counts (actual players, spectators, maximum players)
    @staticmethod
    def parse_players_count(server_data):
        # TODO red_players, blue_players, ffa players (without team), spectators
        spectators = 0
        max_players = server_data['teamsize'] * 2
        players_in_game = server_data['num_players']

        if max_players == 0:
            max_players = server_data['max_clients']

        if 'players' in server_data.keys():
            players = server_data['players']

            for player in players:
                if player['team'] == 3:
                    spectators += 1

            players_in_game = len(players) - spectators

        return players_in_game, spectators, max_players


    ## Gets qlranks.com ELO.
    # @return Dictionary object with elo per game type.
    @staticmethod
    def get_ql_ranks_elo(nick):
        response = requests.get('http://www.qlranks.com/api.aspx?nick=%s' % nick, timeout=10)

        return response.json()['players'][0]


class NetworkStatusListener():
    def network_status_changed(self, new_status):
        raise NotImplementedError('Method not implemented')

    def __init__(self):
        QLNetwork().listeners.append(self)

    def __del__(self):
        QLNetwork().listeners.remove(self)


'''
Following information is based on my own (Victor Polevoy) investigation.

browse servers
You need to send base64-encoded string of json to - http://www.quakelive.com/browser/list?filter=

filter parameter looks like:

    filter = {
        "filters": {
            "group":"any",                      # any | friends ***String***
            "game_type":"any",                  # game_types already listed here ***String***
            "arena":"any",                      # arena complexity=(BASIC | INTERMEDIATE | ADVANCED),
                                                # arena size=(SMALL | MEDIUM | LARGE),
                                                # arena mappool=(QCON08 | QCON09 | QCON10 | QCON11 | QCON12 | QCON13
                                                # | QCON14 | IEM4 | IEM5 | DHS10 | DHW10 | DHS11 | DHW11 | DHS12 | DHW12
                                                # | FIEUL | almostlost(=or any other map name)                  ***String***
            "state":"any",                      # any(=ready to play) | IN_PROGRESS | POPULATED | PRE_GAME(=warmup) | EMPTY(=waiting for players) ***String***
            "difficulty":"any",                 # any | -1(=unrestricted) | 1(=skill matched) | 2(=more challenging) | 3(=very difficult)***String***
            "location":"any",                   # any(=in your vicinity) | ALL(=all locations) | 666(=LanEvent QC BYOC)
                                                # | Africa | Asia | Europe | Oceania | "North America" | "South America"
                                                # for specified location see location list in this file    ***String***
            "private":0,                        # 0(=public matches) | 1(=private matches) | 2(=invited matches)
                                                # needs to set "invitation_only" to 1 when private is 2    ***Integer***
            "premium_only":0,                   # 0 (=false) | 1 (=true - premium only) ***Integer***
            "ranked":"any",                     # 0(=unranked) | 1(=ranked) | "any"
            "invitation_only":0                 # Invites-only server - 0/1 ***Integer***
        },
        "arena_type":"",                        # ""(=any arena) | tag(=filters[arena] is BASIC|INTERMEDIATE|ADVANCED)
        "players":[],                           # filter by player (atm it is possible to filter only by friend
                                                # nicknames) ***List of strings***
        "game_types":[5,4,3,0,1,9,10,11,8,6],   # [1,3,4] | []   - find game_types in this file ***List of integers***
        "ig":0                                  # 0 (=no instagib) | 1(=instagib) | "any"(***string type***)***Integer***
    }

answer from the server looks like (real answer truncated to 2 items):

    {
        "lfg_requests":0,
        "matches_played":19,
        "servers":
            [
                {
                    "num_players":1,
                    "map":"deepinside",
                    "public_id":491267,
                    "ruleset":"1",
                    "location_id":21,
                    "game_type":10,
                    "g_needpass":0,
                    "teamsize":5,
                    "owner":"pinknightmares",
                    "ranked":0,
                    "host_name":"Real Domination",
                    "skillDelta":-1,
                    "g_customSettings":"4751392",
                    "premium":0,
                    "host_address":"199.21.113.50:27032",
                    "max_clients":16,
                    "num_clients":3,
                    "g_instagib":0
                },
                {
                    "num_players":4,
                    "map":"thunderstruck",
                    "public_id":491961,
                    "ruleset":"3",
                    "location_id":25,
                    "game_type":4,
                    "g_needpass":0,
                    "teamsize":5,
                    "owner":"s1gfr1d",
                    "ranked":1,
                    "host_name":"FTS Putos",
                    "skillDelta":-1,
                    "g_customSettings":"0",
                    "premium":1,
                    "host_address":"76.74.236.91:27047",
                    "max_clients":16,
                    "num_clients":5,
                    "g_instagib":0
                }
            ]
    }


Once you've got a server list you may get detailed information about it by sending it's public server id to:
http://www.quakelive.com/browser/details?ids=

ids parameter can be like - 490452

example of answer (json):

    [
        {
            "num_players":0,
            "public_id":490452,
            "ECODE":0,
            "teamsize":3,
            "g_customSettings":"0",
            "g_levelstarttime":1410207366,
            "owner":"fertez",
            "location_id":69,
            "players":
                [
                    {
                        "clan":"^1qlp^7",
                        "sub_level":2,
                        "name":"fertez",
                        "bot":0,
                        "rank":2,
                        "score":0,
                        "team":3,
                        "model":"doom\/sport_blue"
                    }
                ],
            "max_clients":16,
            "roundtimelimit":240,
            "map_title":"Blood Run",
            "scorelimit":"150",
            "ruleset":"3",
            "skillDelta":-1,
            "game_type_title":"Clan Arena",
            "map":"bloodrun",
            "premium":0,
            "g_needpass":0,
            "ranked":1,
            "g_instagib":0,
            "g_bluescore":0,
            "g_gamestate":"PRE_GAME",
            "host_address":"217.18.140.232:27037",
            "fraglimit":20,
            "num_clients":1,
            "capturelimit":8,
            "game_type":4,
            "timelimit":0,
            "roundlimit":7,
            "host_name":"qlp FerteZ",
            "g_redscore":0
        }
    ]

spawn a server:
You need to send json data by POST to: http://www.quakelive.com/startamatch/start

json-post data should look like:

    settings: {
        "invites": [],                                          # No invites to send after server spawn
        "maps": ["ironworks"],                                  # Selected arena: "ironworks"
        "cvars": {
            "g_gametype": 5,                                    # Capture The Flag game
            "g_password": "ctf",                                # Server password - "ctf"
            "sv_hostname": "best+server",                       # Server name - "best server"
            "web_location": "18",                               # Germany, Frankfurt
            "ruleset": 1                                        # Classic mode
        }
    }

    answer is json-data too:

    {
        MSG: "OK",
        TOKEN: "be25fec240b14ec591a58cbadc338875",
        ECODE: 0
    }

get info about spawning server:
    http://www.quakelive.com/startamatch/status?token=be25fec240b14ec591a58cbadc338875

    answer: {
        MSG: "Server is starting",
        ECODE: 2
    }
when server is spawned the result will be:
    answer {
        MSG: "Server is ready",
        SERVER_INFO: {                  #OBJECT
            INVITATION_CODE: '6523316d-5fef-4eee-bc80-720a3ef28ae1',
            SERVER_ID: 488317,
            IP: '91.198.152.121',
            MAP_NAMES: [                #ARRAY
                0: 'ironworks'
            ],
            GAME_TYPE: 'ctf',
            ACCESS: 'public',
            PASSWORD: 'ctf',
            LOCATION_ID: 18,
            PORT: 27010,
        },
        ECODE: 0
    }

server parameters:
    g_game_type =
        1 for ffa
        2 for duel
        3 for tdm
        4 for ca
        5 for ctf
        6 for 1-flag-ctf
        7 for harvester
        8 for ft
        9 for dom
        10 for attack&defend
        11 for redrover
        12 for race

    web_location =
        44 for Russia, Moscow
        18 for Germany, Frankfurt
        17 for Netherlands, Amsterdam
        19 for United Kingdom, Maidenhead
        29 for Sweden, Stockholm


Stop server:
send public server id by post to http://www.quakelive.com/request/stopserver

parameter should look like:

    server_id=492596


get server info by code:
1)
    http://www.quakelive.com/request/rsvp?inv_code=e7173554-8d35-44b4-8297-e85a59ef1b7c

    {"player_id": 486860, "host": "91.198.152.137:27034", "password": "ctf"}
2)
    http://www.quakelive.com/browser/details?ids=485897
[{"num_players":6,"public_id":485897,"ECODE":0,"teamsize":3,"g_customSettings":"0","g_levelstarttime":1410023440,"owner":"falcon75","location_id":44,"players":[{"clan":"^2l^3l^1l","sub_level":0,"name":"shiva","bot":0,"rank":0,"score":7,"team":1,"model":"visor\/default"},{"clan":"","sub_level":0,"name":"fedyapupkin","bot":0,"rank":0,"score":2,"team":2,"model":"doom"},{"clan":"RH*","sub_level":0,"name":"destructo71","bot":0,"rank":0,"score":2,"team":1,"model":"sarge"},{"clan":"","sub_level":0,"name":"acidke","bot":0,"rank":0,"score":2,"team":2,"model":"doom\/default"},{"clan":"","sub_level":0,"name":"saptell","bot":0,"rank":0,"score":0,"team":2,"model":"tankJr\/bright"},{"clan":"","sub_level":0,"name":"ad_augusta","bot":0,"rank":0,"score":2,"team":1,"model":"sarge\/default"}],"max_clients":8,"roundtimelimit":180,"map_title":"Campgrounds","scorelimit":"150","ruleset":"3","skillDelta":-1,"game_type_title":"Clan Arena","map":"campgrounds","premium":0,"g_needpass":0,"ranked":1,"g_instagib":0,"g_bluescore":0,"g_gamestate":"IN_PROGRESS","host_address":"85.21.90.90:27006","fraglimit":20,"num_clients":6,"capturelimit":8,"game_type":4,"timelimit":0,"roundlimit":10,"host_name":"RockU Falcon75","g_redscore":1}]
'''