"""
QuakeLive Launcher
Copyright (C) 2013  Victor Polevoy (vityatheboss@gmail.com)

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

from qllauncher import qlprofile
import re

profile = qlprofile.QLProfile('fx', qlprofile.QLProfileRequestType.SUMMARY, True)


from html import parser as html_parser
parser = html_parser.HTMLParser()
page = qlprofile.QLProfile.get_profile_page('fx', qlprofile.QLProfileRequestType.SUMMARY).text



import xml.etree.ElementTree as ET
# page = page.replace('&hellip;', '...')
parser = ET.XMLParser()
parser.parser.UseForeignDTD(True)
tree = ET.fromstring(page, parser=parser)
# tree = ET.fromstring(page)

profile_title = tree.findall('.//h1[@class="profile_title"]')[0]
profile_title_flag_image = profile_title[0].attrib['src']
profile_title_name = tree[0].text
profile_player_body_image = tree.findall('.//div[@class="prf_imagery"]')[0][0].attrib['style']

matches = re.search('background: url\((.*)\)', profile_player_body_image)
if matches:
    profile_player_body_image = matches.group(1)
stats = tree.findall('.//div[@class="prf_vitals"]/p')[0]
text = str(ET.tostring(stats))
text = text.replace('\\n', '')
text = text.replace('\\t', '')
print('test: ' + text)


print('fx exists?: %s' % qlprofile.QLProfile.is_player_exists('fx'))
print('sadfdsaop23j42 exists?: %s' % qlprofile.QLProfile.is_player_exists('sadfdsaop23j42'))

