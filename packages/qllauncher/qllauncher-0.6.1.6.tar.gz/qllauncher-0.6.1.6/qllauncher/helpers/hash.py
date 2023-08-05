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

from qllauncher.helpers import misc
import platform
import subprocess

## Calculates md5sum of a file in crossplatform-way
# @param file_name Name of the file
# @return MD5 sum string
def md5sum(file_name):
    command = 'md5sum'

    if platform.system() == 'Darwin':
        command = 'md5 -q'

    return subprocess.check_output('%s %s' % (command, misc.cmd_quote(file_name)),
                                   shell=True).decode().splitlines()[0].split(' ')[0]