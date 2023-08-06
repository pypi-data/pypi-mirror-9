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

# Identify and replace placeholder in a path
'''Identify and replace placeholder in a path'''

from datetime import datetime

class PlaceHolder(object):
    '''Identify and replace placeholder in a path'''

    def __init__(self, __path):
        '''The constructor for the PlaceHolder class.

        Keyword arguments:
        __path -- the path of the backup

        '''
        self.__path = __path
        self.__main()

    def __main(self):
        '''Main of the PlaceHolder class'''
        __year, __shortyear, __month, __weeknumber, __monthday, __weekday, __hour, __minute, __second = datetime.now().strftime('%Y %y %m %W %d %w %H %M %S').split()
        # year
        if '%Y' in self.__path:
            self.__path = self.__path.replace('%Y', __year)
        # year in two-digit format
        if '%y' in self.__path:
            self.__path = self.__path.replace('%y', __shortyear)
        # month (1..12)
        if '%m' in self.__path:
            self.__path = self.__path.replace('%m', __month)
        # week number in year (1..52)
        if '%W' in self.__path:
            self.__path = self.__path.replace('%W', __weeknumber)
        # monthday (1..31)
        if '%d' in self.__path:
            self.__path = self.__path.replace('%d', __monthday)
        # weekday first monday (1..7)
        if '%w' in self.__path:
            self.__path = self.__path.replace('%w', __weekday)
        # hour (00..24)
        if '%H' in self.__path:
            self.__path = self.__path.replace('%H', __hour)
        # minute (00..59)
        if '%M' in self.__path:
            self.__path = self.__path.replace('%M', __minute)
        # second (00..59)
        if '%S' in self.__path:
            self.__path = self.__path.replace('%S', __second)

    @property
    def realpath(self):
        '''Return the real path afther placeholder replacement'''
        return self.__path
