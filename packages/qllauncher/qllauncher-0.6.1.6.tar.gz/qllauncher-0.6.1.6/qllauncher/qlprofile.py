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


import requests
import xml.etree.ElementTree as ET
import re
import qllauncher as qll


class QLProfile():
    PROFILE_PAGE_PATTERN = 'http://www.quakelive.com/profile/%s/%s'

    def __init__(self, nick, profile_request_type, parse_immediate=False):
        self._nick = nick
        self._profile_request_type = profile_request_type
        self.data = {}

        if parse_immediate:
            self._parse_profile()

    def _parse_profile(self):
        page = QLProfile.get_profile_page(self._nick, self._profile_request_type)
        parser = QLProfileParser.create_parser(self._profile_request_type)

        self.data = parser.parse_html(page)

    def parse(self):
        self._parse_profile()

    def get_elo(self):
        return qll.QLNetwork.get_ql_ranks_elo(self._nick)

    @staticmethod
    def get_profile_page(nick, profile_request_type):
        return requests.get(QLProfile.PROFILE_PAGE_PATTERN % (profile_request_type, nick))

    @staticmethod
    def is_player_exists(nick):
        return True if requests.post('http://quakelive.com/register/verify/nametag',
                                     data={"value": nick}).json()['ECODE'] == -1 else False


class QLProfileRequestType():
    SUMMARY = 'summary'


class QLProfileParser():
    def parse_html(self, page):
        raise NotImplementedError('ERROR: Method not implemented')

    @staticmethod
    def create_parser(profile_request_type):
        if profile_request_type == QLProfileRequestType.SUMMARY:
            return QLProfileSummaryParser()


class QLProfileSummaryParser(QLProfileParser):
    def __init__(self):
        QLProfileParser.__init__(self)

    def parse_html(self, page):
        try:
            page = page.text
            page = page.replace('&hellip;', '...') # TODO fix parse error with all html  entities
            tree = ET.fromstring(page)
            profile_title = tree.findall('.//h1[@class="profile_title"]')[0]
            profile_title_flag_image = profile_title[0].attrib['src']
            profile_title_name = tree[0].text
            profile_player_body_image = tree.findall('.//div[@class="prf_imagery"]')[0][0].attrib['style']

            matches = re.search('background: url\((.*)\)', profile_player_body_image)
            if matches:
                profile_player_body_image = matches.group(1)
            else:
                profile_player_body_image = ''
            stats = tree.findall('.//div[@class="prf_vitals"]/p')[0]
            text = ET.tostring(stats).decode()
            text = text.replace('\\n', '')
            text = text.replace('\\t', '')

            return {
                'name': profile_title_name,
                'flag': profile_title_flag_image,
                'model': profile_player_body_image,
                'summary': text
            }
        except BaseException as e:
            return None