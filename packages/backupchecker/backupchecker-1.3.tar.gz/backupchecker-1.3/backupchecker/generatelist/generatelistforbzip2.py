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

import bz2
import fnmatch
import os
import os.path
import stat

from backupchecker.checkhashes import get_hash
from backupchecker.generatelist.generatelist import GenerateList

# Generate a list of files from a bzip2 archive
'''Generate a list of files from a bzip2 archive'''

class GenerateListForBzip2(GenerateList):
    '''Generate a list of files from a bzip2 archive'''

    def __init__(self, __genparams):
        '''The constructor for the GenerateListForBzip2 class'''
        __arcpath = __genparams['arcpath']
        __delimiter = __genparams['delimiter']
        self._genfull = __genparams['genfull']
        self.__listoutput = __genparams['listoutput']
        self.__confoutput = __genparams['confoutput']
        self.__fulloutput = __genparams['fulloutput']
        self.__getallhashes  = __genparams['getallhashes']
        self.__hashtype = __genparams['hashtype']
        self.__parsingexceptions = __genparams['parsingexceptions']
        self.__confname = __genparams['confname']
        __listoffiles = ['[files]\n']
        __filetype = 'f'
        __filehash = get_hash(bz2.BZ2File(__arcpath, 'r'), 'md5')
        if self.__getallhashes:
            if not self.__hashtype:
                __onelinewithhash = '{value}{delimiter} type{delimiter}{value} md5{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
            else:
                __onelinewithhash = '{value}{delimiter} type{delimiter}{value} {hashtype}{delimiter}{value}\n'.format(value='{}', hashtype=self.__hashtype, delimiter=__delimiter)
            __listoffiles.append(__onelinewithhash.format(
                                    os.path.split(__arcpath)[-1][:-4],
                                    __filetype,
                                    __filehash))
        else:
            if self.__parsingexceptions :
                for __file in self.__parsingexceptions:
                    if fnmatch.fnmatch(os.path.split(__arcpath)[-1][:-4], __file):
                        __filehash = get_hash(bz2.BZ2File(__arcpath, 'r'), self.__parsingexceptions[__file])
                        __onelinewithhash = '{value}{delimiter} type{delimiter}{value} {hashtype}{delimiter}{value}\n'.format(value='{}', hashtype=self.__parsingexceptions[__file], delimiter=__delimiter)
                        __listoffiles.append(__onelinewithhash.format(
                                                os.path.split(__arcpath)[-1][:-4],
                                                __filetype,
                                                __filehash))
                    else:
                        __onelinewithouthash = '{value}{delimiter} type{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
                        __listoffiles.append(__onelinewithouthash.format(
                                                os.path.split(__arcpath)[-1][:-4],
                                                __filetype))
            else:
                __onelinewithouthash = '{value}{delimiter} type{delimiter}{value}\n'.format(value='{}', delimiter=__delimiter)
                __listoffiles.append(__onelinewithouthash.format(
                                        os.path.split(__arcpath)[-1][:-4],
                                        __filetype))

        # define the flexible file list path
        __arcwithext = os.path.split(''.join([__arcpath[:-3], 'list']))[1]
        if self.__listoutput:
            if self.__confname:
                # --gen-list and --output-list-dir and --configuration-name
                __arclistpath = os.path.join(self.__listoutput, '.'.join([self.__confname, 'list']))
            else:
                # --gen-list and --output-list-dir 
                __arclistpath = os.path.join(self.__listoutput, __arcwithext)
        elif self.__fulloutput:
            if self.__confname:
                # --gen-list and --output-conf-and-list-dir and --configuration-name
                __arclistpath = os.path.join(self.__fulloutput, '.'.join([self.__confname, 'list']))
            else:
                # --gen-list and --output-conf-and-list-dir
                __arclistpath = os.path.join(self.__fulloutput, __arcwithext)
        else:
            # --gen-list only
            if self.__confname:
                __arc = os.path.dirname(__arcpath)
                __arclistpath = os.path.join(__arc, '.'.join([self.__confname, 'list']))
            else:
                __arclistpath = ''.join([__arcpath[:-3], 'list'])
            
        # call the method to write information in a file
        __listconfinfo = {'arclistpath': __arclistpath,
                            'listoffiles':  __listoffiles}
        self.__lci = __listconfinfo
        self._generate_list(__listconfinfo)
        # call the method to write the configuration file if --gen-full was required
        if self._genfull:
            # generate the hash sum of the list of files
            __listhashsum = self._get_list_hash(__listconfinfo['arclistpath'])
            # define the flexible configuration file path
            __arcwithext = os.path.split(''.join([__arcpath[:-3], 'conf']))[1]
            if self.__confoutput:
                if self.__confname:
                    # --gen-full and --output-conf-dir and --configuration-name
                    __arcconfpath = os.path.join(self.__confoutput, '.'.join([self.__confname, 'conf']))
                else:
                    # --gen-full and --output-conf-dir
                    __arcconfpath = os.path.join(self.__confoutput, __arcwithext)
            elif self.__fulloutput:
                if self.__confname:
                    # --gen-full and --output-conf-and-list-dir and --configuration-name
                    __arcconfpath = os.path.join(self.__fulloutput, '.'.join([self.__confname, 'conf']))
                else:
                    # --gen-full and --output-conf-and-list-dir
                    __arcconfpath = os.path.join(self.__fulloutput, __arcwithext)
            else:
                # --gen-full only
                if self.__confname:
                    __arc = os.path.dirname(__arcpath)
                    __arcconfpath = os.path.join(__arc, '.'.join([self.__confname, 'conf']))
                else:
                    __arcconfpath = ''.join([__arcpath[:-3], 'conf'])
            # user-define name of the archive
            if self.__confname:
                __arcname =  self.__confname
            else:
                __arcname =  os.path.basename(__arcpath[:-4])
            __confinfo = {'arcname': __arcname,
                            'arcpath': __arcpath,
                            'arcconfpath': __arcconfpath,
                            'arclistpath': __listconfinfo['arclistpath'],
                            'arctype': 'archive',
                            'sha512': __listhashsum}
            self.__ci = __confinfo
            self._generate_conf(__confinfo)
