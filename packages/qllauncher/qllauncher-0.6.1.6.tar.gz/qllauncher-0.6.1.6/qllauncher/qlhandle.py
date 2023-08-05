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


import urllib.request
import urllib.parse
import re
import os
import requests
import logging
import zipfile

from qllauncher.helpers import hash
from qllauncher import launchers

## Class encapsulates game work.
# Contains: game installer, game updater, arena image extractor, launch the game.
class QLHandle():
    _check_update_regexp = '(.*)http:\/\/cdn.quakelive.com\/assets\/(\d{10})\/QuakeLiveSetup_(\d+).exe(.*)'
    _cdn_update_url_pattern = 'http://cdn.quakelive.com/assets/%s/game/manifest.json'
    _cdn_files_download_url_pattern = 'http://cdn.quakelive.com/assets/%s/%s'
    _check_update_url = 'http://www.quakelive.com/launcher'


    ## Constructor
    # @param executable Full path to "quakelive.exe" file
    # @param home_path Full path to quakelive home path
    # @param base_path Full path to quakelive base path
    # @param gt_user User nick name
    # @param gt_pass User XMPP password (XAID)
    # @param ql_session web quakelive session
    # @param taskset Runs on single core if set to True
    # @param wineskin_path Full path to wineskin wrapper .app file
    def __init__(self,
                 executable,
                 home_path,
                 base_path,
                 gt_user='UnnamedPlayer',
                 gt_pass='',
                 ql_session='',
                 taskset=False,
                 wineskin_path=None):

        self.downloaded_update_size = 0
        self.downloading_file_name = ''
        self._wineskin_path = wineskin_path
        self._executable = executable
        self._home_path = home_path
        self._base_path = base_path
        self._taskset = taskset
        self._ql_session = ql_session
        self._gt_pass = gt_pass
        self._gt_user = gt_user

    ''' Installer && Updater'''
    ## Extracts images of game maps into extract_path
    # @param extract_path A directory where images of game maps will be extracted
    def extract_arenas_images(self, extract_path):
        packages_path = '%s/baseq3/' % self._base_path
        for (dirpath, dirnames, filenames) in os.walk(packages_path):
            for file in filenames:
                file_name, file_extension = os.path.splitext(file)
                if file_extension == '.pk3':
                    try:
                        compressed_package = zipfile.ZipFile('%s/%s' % (packages_path, file))
                    except zipfile.BadZipFile as e:
                        status_str = "Can't read compressed package '%s': %s" % (file, str(e))

                        logging.warning(status_str)

                        continue

                    for file_in_package in compressed_package.namelist():
                        if file_in_package == 'levelshots/%s.jpg' % file_name:
                            if not os.path.exists('%s/%s' % (extract_path, file_in_package)):
                                status_str = 'Extracting arena image: %s/%s to %s' % (file, file_in_package, extract_path)

                                logging.info(status_str)

                                if not os.path.exists(extract_path):
                                    os.makedirs(extract_path)

                                compressed_package.extract(file_in_package, extract_path)

    ## Checks whether game update exists.
    # @return Update date mark (str)
    @staticmethod
    def check_update():
        update_date = None

        response = requests.get(QLHandle._check_update_url)

        content = response.content.decode().split('\n')

        for line in content:
            matches = re.match(QLHandle._check_update_regexp, line)

            if matches:
                update_date = matches.group(2)

        return update_date

    def _get_update_file_location(self, update_item):
        executable_path = self._executable.rsplit('/', 1)[0]

        if update_item['dir']:
            file_location = '%s/%s/%s' % (self._base_path, update_item['dir'], update_item['local'])
        else:
            file_location = '%s/%s' % (executable_path, update_item['local'])

        return file_location

    def _get_update_files_total_size(self, manifest_file):
        if manifest_file:
            files_list = manifest_file['files']
            total_size = 0
            for item in list(files_list):
                real_file_location = self._get_update_file_location(item)

                if os.path.exists(real_file_location) and hash.md5sum(real_file_location) == item['chksum']:
                    files_list.remove(item)
                else:
                    total_size += item['size']

            return total_size

    ## Returns update size of the game update with update mark == update_date
    # @param update_date Update date mark
    # @return Update size in real
    def get_update_size(self, update_date):
        if update_date:
            manifest_file = requests.get(QLHandle._cdn_update_url_pattern % update_date).json()

            return self._get_update_files_total_size(manifest_file)

    ## Downloads game update files with update mark == update_date
    # @param update_date Update date mark
    def get_update_files(self, update_date):
        if update_date:
            response = requests.get(QLHandle._cdn_update_url_pattern % update_date).json()

            files_list = response['files']

            total_size = self._get_update_files_total_size(response)

            total_size /= 1048576
            self.downloaded_update_size = 0.0

            for item in files_list:
                self.downloading_file_name = item['local']
                item_size = item['size'] / 1048576

                save_file_location = self._get_update_file_location(item)
                save_file_directory = save_file_location.rsplit('/', 1)[0]

                if not os.path.exists(save_file_directory):
                    os.mkdir(save_file_directory)

                logging.debug('Downloading "%s"\t%4.2f(MB) (%4.2f(MB) of %4.2f(MB))' % (self.downloading_file_name,
                                                                                        item_size,
                                                                                        self.downloaded_update_size / 1048576,
                                                                                        total_size))

                url = QLHandle._cdn_files_download_url_pattern % (update_date, item['source'])
                u = urllib.request.urlopen(url)
                f = open(save_file_location, 'wb')
                block_sz = 8192
                while True:
                    buffer = u.read(block_sz)
                    if not buffer:
                        break

                    self.downloaded_update_size += len(buffer)
                    f.write(buffer)

                f.close()

    ''' Launcher '''
    ## Launches the game on any platform
    # @param additional_argument An argument that is appended to result process call string.
    def launch(self, additional_argument=None):
        if (self._executable
            and self._home_path
            and self._base_path
            and os.path.exists(self._executable)
            and os.path.exists(self._home_path)
            and os.path.exists(self._base_path)
        ):
            launcher = launchers.create_launcher(executable=self._executable,
                                                 gt_user=self._gt_user,
                                                 gt_pass=self._gt_pass,
                                                 base_path=self._base_path,
                                                 home_path=self._home_path,
                                                 ql_session=self._ql_session,
                                                 taskset=self._taskset,
                                                 additional_argument=additional_argument,
                                                 wineskin_path=self._wineskin_path)
            launcher.launch()
        else:
            raise EnvironmentError('Binary path and/or home path and/or base path is not properly set.')
