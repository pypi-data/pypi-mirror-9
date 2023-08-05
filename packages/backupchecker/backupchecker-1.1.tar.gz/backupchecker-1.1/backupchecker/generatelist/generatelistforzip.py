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

# Generate a list of files from a zip archive
'''Generate a list of files from a zip archive'''

import datetime
import fnmatch
import logging
import os.path
import stat
import sys
import zipfile

from backupchecker.checkhashes import get_hash
from backupchecker.generatelist.generatelist import GenerateList

class GenerateListForZip(GenerateList):
    '''Generate a list of files from a zip archive'''

    def __init__(self, __genparams):
        '''The constructor for the GenerateListForZip class'''
        self.__arcpath = __genparams['arcpath']
        self.__delimiter = __genparams['delimiter']
        self._genfull = __genparams['genfull']
        self.__listoutput = __genparams['listoutput']
        self.__confoutput = __genparams['confoutput']
        self.__fulloutput = __genparams['fulloutput']
        self.__getallhashes  = __genparams['getallhashes']
        self.__hashtype = __genparams['hashtype']
        self.__parsingexceptions = __genparams['parsingexceptions']
        try:
            __zip = zipfile.ZipFile(self.__arcpath, 'r', allowZip64=True)
            self.__main(__zip)
        except zipfile.BadZipfile as _msg:
            __warn = '. You should investigate for a data corruption.'
            logging.warning('{}: {}{}'.format(__self.arcpath, str(__msg), __warn))

    def __main(self, __zip):
        '''Main of the GenerateListForZip class'''
        __listoffiles = ['[files]\n']
        __oneline = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        if self.__getallhashes:
            if not self.__hashtype:
                __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} md5{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
            else:
                __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} {hashtype}{delimiter}{value}\n'.format(value='{}', hashtype=self.__hashtype, delimiter=self.__delimiter)
        else:
            __onelinewithouthash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        __onelinenoexternalattr = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mtime{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        __crcerror = __zip.testzip()
        if __crcerror:
            logging.warning('{} has at least one file corrupted:{}'.format(self.__arcpath, __crcerror))
        else:
            __zipinfo = __zip.infolist()
            for __fileinfo in __zipinfo:
                __fileinfo.filename = self._normalize_path(__fileinfo.filename)
                __uid, __gid = self.__extract_uid_gid(__fileinfo)
                # check if external_attr is available
                if __fileinfo.external_attr != 0:
                    __type = self.__translate_type(__fileinfo.external_attr >> 16)
                    __mode = oct(stat.S_IMODE((__fileinfo.external_attr >> 16))).split('o')[-1]
                    # Prepare a timestamp for the ctime object
                __dt = __fileinfo.date_time
                try:
                    __mtime = float(datetime.datetime(__dt[0],
                                                    __dt[1],
                                                    __dt[2],
                                                    __dt[3],
                                                    __dt[4],
                                                    __dt[5]).timestamp())
                except ValueError as __msg:
                    __warn = 'Issue with timestamp while controlling {} in {}'.format(_fileinfo.filename,_cfgvalues['path'])
                    logging.warning(__warn)
                if __fileinfo.external_attr != 0 and __type == 'f':
                    if self.__getallhashes:
                        if not self.__hashtype:
                            __hash = get_hash(__zip.open(__fileinfo.filename, 'r'), 'md5')
                        else:
                            __hash = get_hash(__zip.open(__fileinfo.filename, 'r'), self.__hashtype)
                        __listoffiles.append(__onelinewithhash.format(__fileinfo.filename,
                                                                str(__fileinfo.file_size),
                                                                str(__uid),
                                                                str(__gid),
                                                                __mode,
                                                                __type,
                                                                __mtime,
                                                                __hash))
                    else:
                        # check if there are exceptions while parsing
                        if self.__parsingexceptions:
                            for __file in self.__parsingexceptions:
                                if fnmatch.fnmatch(__fileinfo.filename, __file):
                                    __hash = get_hash(__zip.open(__fileinfo.filename, 'r'), self.__parsingexceptions[__file])
                                    __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} {hashtype}{delimiter}{value}\n'.format(value='{}', hashtype=self.__parsingexceptions[__file], delimiter=self.__delimiter)
                                    __listoffiles.append(__onelinewithhash.format(__fileinfo.filename,
                                                                            str(__fileinfo.file_size),
                                                                            str(__uid),
                                                                            str(__gid),
                                                                            __mode,
                                                                            __type,
                                                                            __mtime,
                                                                            __hash))
                                else:
                                    # we use exceptions-file option but the file is not concerned by an exception
                                    __listoffiles.append(__onelinewithouthash.format(__fileinfo.filename,
                                                                            str(__fileinfo.file_size),
                                                                            str(__uid),
                                                                            str(__gid),
                                                                            __mode,
                                                                            __type,
                                                                            __mtime))
                        else:
                            # we don't use the --exceptions-file option
                            __listoffiles.append(__onelinewithouthash.format(__fileinfo.filename,
                                                                    str(__fileinfo.file_size),
                                                                    str(__uid),
                                                                    str(__gid),
                                                                    __mode,
                                                                    __type,
                                                                    __mtime))
                elif __fileinfo.external_attr != 0 and __type == 'd':
                    __listoffiles.append(__oneline.format(__fileinfo.filename,
                                                            str(__fileinfo.file_size),
                                                            str(__uid),
                                                            str(__gid),
                                                            __mode,
                                                            __type,
                                                            __mtime))
                else:
                    __listoffiles.append(__onelinenoexternalattr.format(__fileinfo.filename,
                                                            str(__fileinfo.file_size),
                                                            str(__uid),
                                                            str(__gid),
                                                            __mtime))
        # define the flexible file list path
        __arcwithext = os.path.split(''.join([self.__arcpath[:-3], 'list']))[1]
        if self.__listoutput:
            __arclistpath = os.path.join(self.__listoutput, __arcwithext)
        elif self.__fulloutput:
            __arclistpath = os.path.join(self.__fulloutput, __arcwithext)
        else:
            # default
            __arclistpath = ''.join([self.__arcpath[:-3], 'list'])
            
        __listconfinfo = {'arclistpath': __arclistpath,
                            'listoffiles':  __listoffiles}
        # call the method to write the list of files inside the archive
        self._generate_list(__listconfinfo)
        # call the method to write the configuration file if --gen-full was required
        if self._genfull:
            # generate the hash sum of the list of files
            __listhashsum = self._get_list_hash(__listconfinfo['arclistpath'])
            # define the flexible configuration file path
            __arcwithext = os.path.split(''.join([self.__arcpath[:-3], 'conf']))[1]
            if self.__confoutput:
                __arcconfpath = os.path.join(self.__confoutput, __arcwithext)
            elif self.__fulloutput:
                __arcconfpath = os.path.join(self.__fulloutput, __arcwithext)
            else:
                # default
                __arcconfpath = ''.join([self.__arcpath[:-3], 'conf'])
            __arcname =  os.path.basename(self.__arcpath[:-4])
            __confinfo = {'arcname': __arcname,
                            'arcpath': self.__arcpath,
                            'arcconfpath': __arcconfpath,
                            'arclistpath': __listconfinfo['arclistpath'],
                            'arctype': 'archive',
                            'sha512': __listhashsum}
            self._generate_conf(__confinfo)

    def __extract_uid_gid(self, __binary):
        '''Extract uid and gid from a zipinfo.extra object (platform dependant)'''
        __uid, __gid = int.from_bytes(__binary.extra[15:17], sys.byteorder), \
                            int.from_bytes(__binary.extra[20:22], sys.byteorder)
        return (__uid, __gid)

    def __translate_type(self, __mode):
        '''Translate the type of the file to a generic name'''
        if stat.S_ISREG(__mode):
            return 'f'
        elif stat.S_ISDIR(__mode):
            return 'd'
