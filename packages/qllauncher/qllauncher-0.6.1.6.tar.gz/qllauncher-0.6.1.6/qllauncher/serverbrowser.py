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


import requests

from qllauncher import qlnetwork


class ServerBrowser():

    # only for server browser filter
    filter_game_types = {
        'any': {
            'title': 'All Game Types',
            'values': {},
        },

        "12": {
            'title': 'Any Ranked Game',
            'values': {
                "16": '1-Flag CTF (1FCTF)',
                "18": 'Attack & Defend (A&D)',
                "3": 'Capture The Flag (CTF)',
                "4": 'Clan Arena (CA)',
                "15": 'Domination (DOM)',
                "7": 'Duel',
                "2": 'Free For All (FFA)',
                "5": 'Freeze Tag (FT)',
                "17": 'Harvester (HAR)',
                "25": 'Race',
                "19": 'Red Rover (RR)',
                "6": 'Team Deathmatch (TDM)',
            },
        },

        '1': {
            'title': 'Any Team Game',
            'values': {},
        },

        '13': {
            'title': 'Any Unranked Game',
            'values': {
                '8': 'Instagib FFA',
                '21': 'Insta1FCTF',
                '23': 'InstaA&D',
                '14': 'InstaCA',
                '9': 'InstaCTF',
                '20': 'InstaDOM',
                '10': 'InstaFreeze',
                '22': 'InstaHAR',
                '24': 'InstaRR',
                '11': 'InstaTDM',
            }
        }
    }

    blank_filter = {
        "filters": {
            "group":"any",
            "game_type":'any',
            "arena":"any",
            "state":"any",
            "difficulty":"any",
            "location":"any",
            "private":0,
            "premium_only":0,
            "ranked":"any",
            "invitation_only":0
        },
        "arena_type":"",
        "players":[],
        "game_types":['any'],
        "ig":0
    }

    FILTERS_GROUP = {
        'any': 'Any Players',
        'friends': 'My Friends',
    }

    FILTERS_ARENA = [
        'any',

        # arena complexity
        'BASIC',
        'INTERMEDIATE',
        'ADVANCED',

        # arena size
        'SMALL',
        'MEDIUM',
        'LARGE',

        # mappool
        'QCON08',
        'QCON09',
        'QCON10',
        'QCON11',
        'QCON12',
        'QCON13',
        'QCON14',
        'IEM4',
        'IEM5',
        'DHS10',
        'DHW10',
        'DHS11',
        'DHW11',
        'DHS12',
        'DHW12'
    ]

    FILTERS_STATE = {
        'any': 'Ready to Play',

        'IN_PROGRESS': 'In-Progress',
        'POPULATED': 'All Populated',
        'PRE_GAME': 'Pre-Game Warmup',
        'EMPTY': 'Waiting For Players (Empty)',
    }

    FILTERS_DIFFICULTY = {
        'any': 'Any Difficulty',

        -1: 'Unrestricted',
        1: 'Skill Matched',
        2: 'More Challenging',
        3: 'Very Difficult',
    }

    FILTERS_PRIVATE = {
        0: 'Public',
        1: 'Private',
        2: 'Invited',
    }

    FILTERS_PREMIUM_ONLY = [
        0,
        1
    ]

    FILTERS_RANKED = [
        'any',

        0,
        1
    ]

    FILTERS_INSTAGIB = {
        0: 'No InstaGib',
        1: 'InstaGib',
    }

    FILTERS_INVITATION_ONLY = [
        0,
        1
    ]

    FILTERS_ARENA_TYPE = [
        '',
        'tag'
    ]

    ## Creates server browser filter dictionary.
    # @return Server filter dictionary.
    @staticmethod
    def create_server_browser_filter(group='any',
                                     game_type='any',
                                     arena='any',
                                     state='any',
                                     difficulty='any',
                                     location='any',
                                     private=0,
                                     premium_only=0,
                                     ranked='any',
                                     invitation_only=0,
                                     arena_type='',
                                     players='',
                                     game_types='',
                                     ig=0):
        if (group not in ServerBrowser.FILTERS_GROUP.keys()
            or (game_type not in qlnetwork.QLNetwork.game_types)
            or arena not in ServerBrowser.FILTERS_ARENA
            or state not in ServerBrowser.FILTERS_STATE.keys()
            or difficulty not in ServerBrowser.FILTERS_DIFFICULTY.keys()
            or (location not in qlnetwork.QLNetwork.locations)
            or private not in ServerBrowser.FILTERS_PRIVATE.keys()
            or premium_only not in ServerBrowser.FILTERS_PREMIUM_ONLY
            or ranked not in ServerBrowser.FILTERS_RANKED
            or invitation_only not in ServerBrowser.FILTERS_INVITATION_ONLY
            or arena_type not in ServerBrowser.FILTERS_ARENA_TYPE
            or ig not in ServerBrowser.FILTERS_INSTAGIB.keys()):
                raise(AttributeError('Wrong filter parameter'))

        if ig == 1:
            if game_type == 'any':
                game_type = '13'
                game_types = list(qlnetwork.QLNetwork.game_types_unranked.keys())
        else:
            game_types = [game_type]

        return {
            "filters": {
                "group": group,
                "game_type": game_type,
                "arena": arena,
                "state": state,
                "difficulty": difficulty,
                "location": location,
                "private": private,
                "premium_only": premium_only,
                "ranked": ranked,
                "invitation_only": invitation_only
            },
            "arena_type": arena_type,
            "players": players,
            "game_types": game_types,
            "ig": ig
        }

    ## Gets detailed server info by server public id
    # @param server_public_id Public id of the server
    # @return Dictionary object with detailed server info.
    @staticmethod
    def get_detailed_info(server_public_id):
        response = requests.get('http://www.quakelive.com/browser/details?ids=%s' % server_public_id)

        return response.json()
