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

# Extract from the parsing exceptions file the exceptions to comply with
'''Extract from the parsing exceptions file the exceptions to comply with'''

import configparser
from hashlib import algorithms_guaranteed
import os.path
import sys

class ExceptionsParsing:
    '''The ExceptionsParsing class'''

    def __init__(self, __filepath, __delimiter):
        '''The constructor for the ExceptionsParsing class
        '''
        self.__parsingexceptions = {}
        self.__delimiter = __delimiter
        self.__main(__filepath)

    def __main(self, __filepath):
        '''Main for ExceptionsFile class'''
        try:
            with open(__filepath, 'r') as __exceptfile:
                self.__retrieve_data(__exceptfile)
        except (configparser.Error, IOError, OSError) as __err:
            print(__err)
            sys.exit(1)

    def __retrieve_data(self, __file):
        '''Retrieve data from the expected files'''
        # Using default delimiter
        __config = configparser.ConfigParser(delimiters=(self.__delimiter,))
        __config.optionxform = str
        __config.read_file(__file)
        if __config.has_section('files'):
            __files = __config.items('files')
            for __fileitems in __files:
                if __fileitems[0].endswith('/'):
                    self.__parsingexceptions[__fileitems[0][:-1]] = ''
                    __key = __fileitems[0][:-1]
                else:
                    self.__parsingexceptions[__fileitems[0]] = ''
                    __key = __fileitems[0]
                if len(__fileitems) == 2:
                    for __item in __fileitems[1].split(' '):
                            # Test if a hash is provided for this file
                            for __hash in algorithms_guaranteed:
                                if __item.startswith('{}'.format(__hash)):
                                    self.__parsingexceptions[__key] = __item

    @property
    def exceptions(self):
        '''Return the parsing exceptions'''
        return self.__parsingexceptions
