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

# Generate a list of files from a tar archive
'''Generate a list of files from a tar archive'''

import fnmatch
import logging
import os
import os.path
import sys
import tarfile

from backupchecker.generatelist.generatelist import GenerateList
from backupchecker.checkhashes import get_hash

class GenerateListForTar(GenerateList):
    '''Generate a list of files from a tar archive'''

    def __init__(self, __genparams):
        '''The constructor for the GenerateListForTar class'''
        self.__arcpath = __genparams['arcpath']
        self.__delimiter = __genparams['delimiter']
        self._genlist = __genparams['genlist']
        self._genfull = __genparams['genfull']
        self.__listoutput = __genparams['listoutput']
        self.__confoutput = __genparams['confoutput']
        self.__fulloutput = __genparams['fulloutput']
        self.__getallhashes  = __genparams['getallhashes']
        self.__hashtype = __genparams['hashtype']
        self.__parsingexceptions = __genparams['parsingexceptions']
        self.__isastream = __genparams['isastream']
        self.__confname = __genparams['confname']
        try:
            if self.__isastream:
                self.__tarstreamname = 'tarstream'
                self.__streampath = os.path.join(self.__arcpath, self.__tarstreamname)
                __tar = tarfile.open(mode='r|*', fileobj=sys.stdin.buffer)
            else:
                __tar = tarfile.open(self.__arcpath, 'r')
            self.__main(__tar)
        except (tarfile.TarError, EOFError) as _msg:
            __warn = '. You should investigate for a data corruption.'
            logging.warning('{}: {}{}'.format(self.__arcpath, str(_msg), __warn))

    def __main(self, __tar):
        '''Main for the GenerateListForTar class'''
        # extract mtime of the archive
        if not self.__isastream:
            __arcstat = os.stat(self.__arcpath)
            __listoffiles = ['[archive]\nmtime{} {}\n\n[files]\n'.format(self.__delimiter,__arcstat.st_mtime)]
        else:
            __listoffiles = ['[files]\n']
        __oneline = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} owner{delimiter}{value} group{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        if self.__getallhashes:
            # we get all the hash sums of files inside the backup
            if not self.__hashtype:
                __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} owner{delimiter}{value} group{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} md5{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
            else:
                # we switch the default hash sum
                __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} owner{delimiter}{value} group{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} {hashtype}{delimiter}{value}\n'.format(value='{}', hashtype=self.__hashtype, delimiter=self.__delimiter)
        else:
            __onelinewithouthash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} owner{delimiter}{value} group{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        __onelinewithtarget = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} owner{delimiter}{value} group{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} target{delimiter}{value}\n'.format(value='{}', delimiter=self.__delimiter)
        for __tarinfo in __tar:
            # Pick up tar information
            __tarinfo.name = self._normalize_path(__tarinfo.name)
            __type = self.__translate_type(__tarinfo.type)
            __mode = oct(__tarinfo.mode).split('o')[-1]
            # if the file has no right, need to manipulate the output - solving #15
            if __mode == '0':
                __mode = '000'
            if __type == 'f':
                if self.__getallhashes:
                    # extract all hash sums from the archive
                    if not self.__hashtype:
                        # extract hash sum of the file inside the archive
                        __hash = get_hash(__tar.extractfile(__tarinfo.name), 'md5')
                    else:
                        # switch the default hash sum type
                        __hash = get_hash(__tar.extractfile(__tarinfo.name), self.__hashtype)
                    # format the retrieved information
                    __listoffiles.append(__onelinewithhash.format(__tarinfo.name,
                                                            str(__tarinfo.size),
                                                            str(__tarinfo.uid),
                                                            str(__tarinfo.gid),
                                                            str(__tarinfo.uname),
                                                            str(__tarinfo.gname),
                                                            __mode,
                                                            __type,
                                                            float(__tarinfo.mtime),
                                                            __hash,
                                                            __tarinfo.linkname))
                else:
                    # check if there are exceptions while parsing
                    if self.__parsingexceptions:
                        for __file in self.__parsingexceptions:
                            if fnmatch.fnmatch(__tarinfo.name, __file):
                                __hash = get_hash(__tar.extractfile(__tarinfo.name), self.__parsingexceptions[__file])
                                __onelinewithhash = '{value}{delimiter} ={value} uid{delimiter}{value} gid{delimiter}{value} owner{delimiter}{value} group{delimiter}{value} mode{delimiter}{value} type{delimiter}{value} mtime{delimiter}{value} {hashtype}{delimiter}{value}\n'.format(value='{}', hashtype=self.__parsingexceptions[__file], delimiter=self.__delimiter)
                                __listoffiles.append(__onelinewithhash.format(__tarinfo.name,
                                                                        str(__tarinfo.size),
                                                                        str(__tarinfo.uid),
                                                                        str(__tarinfo.gid),
                                                                        str(__tarinfo.uname),
                                                                        str(__tarinfo.gname),
                                                                        __mode,
                                                                        __type,
                                                                        float(__tarinfo.mtime),
                                                                        __hash,
                                                                        __tarinfo.linkname))
                            else:
                                # we use exceptions-file option but the file is not concerned by an exception
                                __listoffiles.append(__onelinewithouthash.format(__tarinfo.name,
                                                                        str(__tarinfo.size),
                                                                        str(__tarinfo.uid),
                                                                        str(__tarinfo.gid),
                                                                        str(__tarinfo.uname),
                                                                        str(__tarinfo.gname),
                                                                        __mode,
                                                                        __type,
                                                                        float(__tarinfo.mtime),
                                                                        __tarinfo.linkname))
                    else:
                        # we don't use the --exceptions-file option
                        __listoffiles.append(__onelinewithouthash.format(__tarinfo.name,
                                                                str(__tarinfo.size),
                                                                str(__tarinfo.uid),
                                                                str(__tarinfo.gid),
                                                                str(__tarinfo.uname),
                                                                str(__tarinfo.gname),
                                                                __mode,
                                                                __type,
                                                                float(__tarinfo.mtime),
                                                                __tarinfo.linkname))
            elif __type == 'l' or __type == 's':
                # format the retrieved information
                __listoffiles.append(__onelinewithtarget.format(__tarinfo.name,
                                                        str(__tarinfo.size),
                                                        str(__tarinfo.uid),
                                                        str(__tarinfo.gid),
                                                        str(__tarinfo.uname),
                                                        str(__tarinfo.gname),
                                                        __mode,
                                                        __type,
                                                        float(__tarinfo.mtime),
                                                        __tarinfo.linkname))
            else:
                # if file is not regular file, ignoring its hash sum
                __listoffiles.append(__oneline.format(__tarinfo.name,
                                                        str(__tarinfo.size),
                                                        str(__tarinfo.uid),
                                                        str(__tarinfo.gid),
                                                        str(__tarinfo.uname),
                                                        str(__tarinfo.gname),
                                                        __mode,
                                                        __type,
                                                        float(__tarinfo.mtime)))

        # Compose the name of the generated list
        ### for tar archive
        if self.__arcpath.lower().endswith('.tar'):
            self.__make_conf_and_list_paths('.tar')
        ### for tar.gz archive
        elif self.__arcpath.lower().endswith('.tar.gz'): 
            self.__make_conf_and_list_paths('.tar.gz')
        ### for tar.bz2 archive
        elif self.__arcpath.lower().endswith('.tar.bz2'):
            self.__make_conf_and_list_paths('.tar.bz2')
        ### for tar.xz archive
        elif self.__arcpath.lower().endswith('.tar.xz'):
            self.__make_conf_and_list_paths('.tar.xz')
        ### for tgz archive
        elif self.__arcpath.lower().endswith('.tgz'):
            self.__make_conf_and_list_paths('.tgz')
        ### for tbz archive
        elif self.__arcpath.lower().endswith('.tbz'):
            self.__make_conf_and_list_paths('.tbz')
        ### for tbz2 archive
        elif self.__arcpath.lower().endswith('.tbz2'):
            self.__make_conf_and_list_paths('.tbz2')
        ### for tar stream
        elif self.__isastream:
            #if self._genfull:
            #    self.__arcname = self.__tarstreamname
            #if self.__confname:
            #    self.__arcname = self.__confname
            #    self.__arcconfpath = ''.join([self.__confname, '.conf'])
            #    self.__arclistpath = ''.join([self.__confname, '.list'])
            #else:
            #    self.__arcconfpath = ''.join([self.__streampath, '.conf'])
            #    self.__arclistpath = ''.join([self.__streampath, '.list'])
            self.__make_conf_and_list_paths('')

        # call the method to write information in a file
        __listconfinfo = {'arclistpath': self.__arclistpath,
                                'listoffiles':__listoffiles}
        self._generate_list(__listconfinfo)
        # call the method to write the configuration file if --gen-full was required
        if self._genfull:
            # generate the hash sum of the list of files
            __listhashsum = self._get_list_hash(__listconfinfo['arclistpath'])
            if self.__isastream:
                __confinfo = {'arcname':self.__arcname,
                                'arcconfpath': self.__arcconfpath,
                                'arclistpath': self.__arclistpath,
                                'arctype': 'archive',
                                'sha512': __listhashsum}
            else:
                __confinfo = {'arcname':self.__arcname,
                                'arcpath':self.__arcpath,
                                'arcconfpath': self.__arcconfpath,
                                'arclistpath': self.__arclistpath,
                                'arctype': 'archive',
                                'sha512': __listhashsum}
            self._generate_conf(__confinfo,self.__isastream)

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

    def __make_conf_and_list_paths(self, __tartype):
        '''Make conf file path and list file paths'''
        if not self.__isastream:
            __arcwithext = os.path.split(self.__arcpath[:-(len(__tartype)-1)])[1]
        # behaviour for --gen-list option
        # define custom path for the filelist or use the default one
        if self.__listoutput:
            # --gen-list and --output-list-dir and --configuration-name
            if self.__confname:
                self.__arclistpath = os.path.join(self.__listoutput, ''.join([self.__confname, '.', 'list']))
            # --gen-list and --output-list-dir
            else:
                if self.__isastream:
                    self.__arclistpath = os.path.join(self.__listoutput, '.'.join([self.__tarstreamname, 'list']))
                else:
                    self.__arclistpath = os.path.join(self.__listoutput, ''.join([__arcwithext, 'list']))
        # define custom path for both filelist and conflist
        elif self.__fulloutput:
            # --gen-list and --output-list-and-conf-dir and --configuration-name
            if self.__confname:
                self.__arclistpath = os.path.join(self.__fulloutput, ''.join([self.__confname, '.', 'list']))
            else:
                # --gen-list and --ouput-list-and-conf-dir
                if self.__isastream:
                    self.__arclistpath = os.path.join(self.__fulloutput, '.'.join([self.__tarstreamname, 'list']))
                else:
                    self.__arclistpath = os.path.join(self.__fulloutput, ''.join([__arcwithext, 'list']))
        else:
            # only --configuration-name
            if self.__confname:
                __arcpath = os.path.dirname(self.__arcpath)
                __arcpath = os.path.join(__arcpath, self.__confname)
                self.__arclistpath = ''.join([__arcpath, '.', 'list'])
            # default behaviour
            else:
                if self.__isastream:
                    __arcdir = os.path.dirname(self.__arcpath)
                    self.__arclistpath = os.path.join(__arcdir, '.'.join([self.__tarstreamname, 'list']))
                else:
                    self.__arclistpath = ''.join([self.__arcpath[:-(len(__tartype)-1)], 'list'])
        # behaviour for --gen-full option
        if self._genfull:
            # define custom path for the conf file
            if self.__confoutput:
                if self.__confname:
                    # --gen-full and --output-conf-dir and --configuration-name
                    self.__arcconfpath = os.path.join(self.__confoutput, ''.join([self.__confname, '.', 'conf']))
                else:
                    # --gen-full and --output-conf-dir
                    if self.__isastream:
                        self.__arcconfpath = os.path.join(self.__confoutput, '.'.join([self.__tarstreamname, 'conf']))
                    else:
                        self.__arcconfpath = os.path.join(self.__confoutput, ''.join([__arcwithext, 'conf']))
            elif self.__fulloutput:
                # --gen-full and --output-list-and-conf-dir and --configuration-name
                if self.__confname:
                    self.__arcconfpath = os.path.join(self.__fulloutput, ''.join([self.__confname, '.', 'conf']))
                else:
                    # --gen-full and --output-list-and-conf-dir
                    if self.__isastream:
                        self.__arcconfpath = os.path.join(self.__fulloutput, '.'.join([self.__tarstreamname, 'conf']))
                    else:
                        self.__arcconfpath = os.path.join(self.__fulloutput, ''.join([__arcwithext, 'conf']))
            else:
                # --gen-full and --configuration-name
                if self.__confname:
                    __arcpath = os.path.dirname(self.__arcpath)
                    __arcpath = os.path.join(__arcpath, self.__confname)
                    self.__arcconfpath = ''.join([__arcpath, '.', 'conf'])
                else:
                    # only --gen-full
                    if self.__isastream:
                        __arcdir = os.path.dirname(self.__arcpath)
                        self.__arcconfpath = os.path.join(__arcdir, '.'.join([self.__tarstreamname, 'conf']))
                    else:
                        self.__arcconfpath = ''.join([self.__arcpath[:-(len(__tartype)-1)], 'conf'])
            # user-defined name of the archive/stream
            if self.__confname:
                self.__arcname = self.__confname
            else:
                if self.__isastream:
                    self.__arcname = self.__tarstreamname
                else:
                    self.__arcname = os.path.basename(self.__arcpath[:-len(__tartype)])

