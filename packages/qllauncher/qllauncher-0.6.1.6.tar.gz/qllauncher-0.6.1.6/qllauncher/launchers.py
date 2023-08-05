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

import platform
import subprocess
import plistlib
import os

from qllauncher.helpers import misc

## Abstract interface for all game launchers.
#


class Launcher():
    ## Constructor gets a dictionary with game parameters to be able to launch the game.
    # The dictionary sets to __dict__ and all dictionary items becomes a object-members.
    def __init__(self, qlhandle_params: dict):
        self.__dict__ = qlhandle_params

    ## Abstract method. All derived classes must launch the game in this method.
    def launch(self):
        raise NotImplementedError('Launch algorithm is not implemented for %s.' % type(self).__class__.__name__)

## Game launcher for linux platform.
# Uses wine as backend and taskset for tuning performance.
class LinuxLauncher(Launcher):
    def __init__(self, qlhandle_params: dict):
        Launcher.__init__(self, qlhandle_params)

    def launch(self):
        launch_prefix = ''

        if self.taskset:
            launch_prefix = 'taskset 0x01'

        additional_argument = ''

        if self.additional_argument:
            additional_argument = self.additional_argument

        subprocess.call('%s wine %s +set gt_realm "quakelive" +set gt_user "%s" +set gt_pass "%s" %s '
                        '+set fs_basepath %s +set fs_homepath %s +set web_sess quakelive_sess=%s '
                        '%s < /dev/null > /dev/null 2>&1 &'
                        % (launch_prefix,
                           misc.cmd_quote(self.executable),
                           self.gt_user,
                           self.gt_pass,
                           '+gt_connect' if self.gt_pass else '',
                           misc.cmd_quote(self.base_path),
                           misc.cmd_quote(self.home_path),
                           self.ql_session,
                           additional_argument)
                        , stdin=None
                        , stdout=None
                        , stderr=None
                        , close_fds=True
                        , shell=True)

## Game launcher for Mac OS X platform.
# Uses wineskin as backend.
class MacLauncher(Launcher):
    def __init__(self, qlhandle_params: dict):
        Launcher.__init__(self, qlhandle_params)

    ## Sets information in wineskin wrapper's .app/plist file to be able to launch the game.
    def _correct_params(self):
        additional_argument = ''

        if self.additional_argument:
            additional_argument = self.additional_argument

        # launch_prefix = ''
        #
        # if self.taskset:
        #     launch_prefix = 'taskset 0x01'      # TODO hprefs/wineskin

        params = '+set gt_realm "quakelive" +set gt_user "%s" +set gt_pass "%s" %s ' \
                 '+set fs_basepath %s +set fs_homepath %s +set web_sess quakelive_sess=%s %s'\
                 % (self.gt_user,
                    self.gt_pass,
                   '+gt_connect' if self.gt_pass else '',
                    misc.cmd_quote(self.base_path),
                    misc.cmd_quote(self.home_path),
                    self.ql_session,
                    additional_argument)

        plist_path = '%s/Contents/Info.plist' % self.wineskin_path
        plist_file = plistlib.readPlist(plist_path) # TODO readPlist -> load
        plist_file['Program Flags'] = params
        symlink_path = '%s/ql' % self.wineskin_path

        os.remove(symlink_path)
        os.symlink(self.base_path, symlink_path)

        plist_file['Program Name and Path'] = '/ql/quakelive.exe'
        plistlib.writePlist(plist_file, plist_path) # TODO writePlist -> dump

    def launch(self):
        if self.wineskin_path:
            self._correct_params()

            subprocess.call('open %s < /dev/null > /dev/null 2>&1 &' % self.wineskin_path
                            , stdin=None
                            , stdout=None
                            , stderr=None
                            , close_fds=True
                            , shell=True)
        else:
            raise EnvironmentError('Wineskin wrapper path is not set.')


class WindowsLauncher(Launcher):
    def __init__(self, qlhandle_params: dict):
        Launcher.__init__(self, qlhandle_params)

    def launch(self):
        print('launching on windows')

## Return a launcher for current user platform.
def create_launcher(**kwargs):
    system = platform.system()
    qlhandle_params = kwargs

    if system == 'Darwin':
        return MacLauncher(qlhandle_params)
    elif system == 'Linux':
        return LinuxLauncher(qlhandle_params)
    elif system == 'Windows':
        return WindowsLauncher(qlhandle_params)