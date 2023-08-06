# -*- coding: utf-8 -*-
# Copyright © 2015 Carl Chenet <chaica@backupcheckerproject.org>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Check a tar archive
'''Check a tar archive'''

import logging
import sys
import tarfile

from backupchecker.expectedvalues import ExpectedValues
from backupchecker.checkbackups.checkarchive import CheckArchive

class CheckTar(CheckArchive):
    '''Check a tar archive'''

    def _main(self, _cfgvalues, _options):
        '''Main for CheckTar'''
        _data = []
        _data, __arcdata = ExpectedValues(_cfgvalues, _options).data
        if _options.isastream:
            __isastream = True
        else:
            __isastream = False
        #########################
        # Test the archive itself
        #########################
        if  not __isastream:
            self._archive_checks(__arcdata, _cfgvalues['path'])
        ###############################
        # Test the files in the archive
        ###############################
        if _data:
            try:
                if __isastream:
                    self._tar = tarfile.open(mode='r|*',fileobj=sys.stdin.buffer)
                else:
                    self._tar = tarfile.open(_cfgvalues['path'], 'r')
                for _tarinfo in self._tar:
                    _tarinfo.name = self._normalize_path(_tarinfo.name)
                    __type = self.__translate_type(_tarinfo.type)
                    __arcinfo = {'path':_tarinfo.name, 'size':_tarinfo.size, 
                                    'uid':_tarinfo.uid, 'gid':_tarinfo.gid,
                                    'uname':_tarinfo.uname, 'gname':_tarinfo.gname,
                                    'mode':_tarinfo.mode, 'type': __type,
                                    'target':_tarinfo.linkname, 'mtime':_tarinfo.mtime}
                    _data = self._check_path(__arcinfo, _data)
                self._missing_files = [_file['path'] for _file in _data]
            except (tarfile.TarError, EOFError) as _msg:
                __warn = '. You should investigate for a data corruption.'
                logging.warning('{}: {}{}'.format(_cfgvalues['path'], str(_msg), __warn))

    def __translate_type(self, __arctype):
        '''Translate the type of the file inside the tar by a generic
        name
        '''
        __types = {tarfile.REGTYPE: 'f',
            tarfile.AREGTYPE: 'a',
            tarfile.CHRTYPE: 'c',
            tarfile.DIRTYPE: 'd',
            tarfile.LNKTYPE: 'l',
            tarfile.SYMTYPE: 's',
            tarfile.CONTTYPE: 'n',
            tarfile.BLKTYPE: 'b',
            tarfile.GNUTYPE_SPARSE: 'g',
            tarfile.FIFOTYPE: 'o'}
        return __types[__arctype]

    def _extract_stored_file(self, __arcfilepath):
        '''Extract a file from the archive and return a file object'''
        __file = self._tar.extractfile(__arcfilepath)
        return __file
