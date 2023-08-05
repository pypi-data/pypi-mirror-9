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

# Retrieve the command line options
'''Retrieve the command line options'''

import logging
from argparse import ArgumentParser
import os
import sys
from hashlib import algorithms_guaranteed

from backupchecker.applogger import AppLogger

class CliParse:
    '''Retrieve the command line options'''

    def __init__(self):
        '''The constructor for the CliParse class.'''
        self._options = ()
        backupcheckerdescription = 'Fully automated backup checker'
        backupcheckerepilog = 'For more information: http://www.backupcheckerproject.org'
        __parser = ArgumentParser(prog='backupchecker',
                                    description=backupcheckerdescription,
                                    epilog=backupcheckerepilog)
        self.__define_options(__parser)

    def __define_options(self, __parser):
        '''Define the options'''
        # define mutually exclusive arguments
        __group = __parser.add_mutually_exclusive_group(required=True)
        __group.add_argument('-c', '--configpath', dest='confpath',
            action='store',
            default=os.getcwd(),
            help='the path to the configurations',
            metavar='DIR')
        __parser.add_argument('-C', '--output-conf-dir', dest='confoutput',
            action='store',
            default='',
            help='the directory to store the configuration file',
            metavar='DIR')
        __parser.add_argument('-d', '--delimiter', dest='delimiter',
            action='store',
            default='|',
            help='delimiter of the fields for the list of files',
            metavar='DELIMITER')
        __parser.add_argument('-E', '--exceptions-file', dest='parsingexceptions',
            action='store',
            default='',
            help='the file with exceptions to normal Brebis behaviour while generating configuration files',
            metavar='FILE')
        __group.add_argument('-g', '--gen-list', dest='genlist',
            action='store_true',
            help='generate a list of files inside a backup')
        __group.add_argument('-G', '--gen-full', dest='genfull',
            action='store_true',
            help='generate the configuration file and the list of files for the backup')
        __parser.add_argument('-H', '--hashes', dest='getallhashes',
            action='store_true',
            help='generate the hash sum of each encountered file in the backup')
        __parser.add_argument('--hashtype', dest='hashtype',
            action='store',
            default='',
            help='the type of the hash sum to use while generating configurations for the archive',
            metavar='HASHTYPE')
        __parser.add_argument('-l', '--log', dest='logfile',
            action='store',
            default=os.path.join(os.getcwd(), 'a.out'),
            help='the log file',
            metavar='FILE')
        __parser.add_argument('-L', '--output-list-dir', dest='listoutput',
            action='store',
            default='',
            help='the directory to store the list of files inside an archive or tree',
            metavar='DIR')
        __parser.add_argument('-O', '--output-list-and-conf-dir', dest='fulloutput',
            action='store',
            default='',
            help='the directory to store the configuration file and the list of files inside an archive or tree',
            metavar='DIR')
        __parser.add_argument('-v', '--version',
            action='version',
            version='%(prog)s 1.0',
            help='print the version of this program and exit')
        __parser.add_argument('archives', nargs='*',
            help='archives to check')
        __args = __parser.parse_args()
        self.__verify_options(__args)

    def __verify_options(self, __options):
        '''Verify the options given on the command line'''
        # check if the archives exist
        for __i, __path in enumerate(__options.archives):
            if not os.path.exists(__path):
                print('{} : no file or directory at this path. Exiting.'.format(__path))
                sys.exit(1)
            else:
                # using absolute path in order to be consistent
                __path = os.path.abspath(__path)
                # if the path exists, check if it is a regular file, a link or
                # a directory otherwise exits
                if not os.path.isfile(__path) and not os.path.isdir(__path):
                    print('{}: not a file or a directory. Exiting.'.format(__path))
                    sys.exit(1)
                else:
                    __options.archives[__i] = __path
        # Check the logfile
        __logdir = os.path.split(__options.logfile)[0]
        if __logdir and not os.path.exists(__logdir):
            print('The directory where to write the log file {} does not exist'.format(__logdir))
            sys.exit(1)
        # Check the exceptions parsing file
        __parsingexceptions = os.path.split(__options.parsingexceptions)[0]
        if __parsingexceptions and not os.path.exists(__parsingexceptions):
            print('The file with exceptions to comply while generating configurations file {} does not exist'.format(__parsingexceptions))
            sys.exit(1)
        # Check the configuration output directory
        __confoutput = __options.confoutput
        if __confoutput and not os.path.exists(__confoutput):
            print('The directory where to write the configuration file {} does not exist'.format(__confoutput))
            sys.exit(1)
        # Check the directory where the list of files is written
        __listoutput= __options.listoutput
        if __listoutput and not os.path.exists(__listoutput):
            print('The directory where to write the list of files inside the archive {} does not exist'.format(__listoutput))
            sys.exit(1)
        # Check the directory where the list of files and the configuration are written
        __fulloutput= __options.fulloutput
        if __fulloutput and not os.path.exists(__fulloutput):
            print('The directory where to write the list of files inside the archive and the configuration file {} does not exist'.format(__fulloutput))
            sys.exit(1)
        # using absolute path in order to be consistent
        __options.logfile = os.path.abspath(__options.logfile)
        # Configure the logger
        AppLogger(__options.logfile)
        # Verify if --gen-list option is not invoked before calling configuration path control
        if not __options.genlist:
            # Check the configuration directory or file
            if not os.path.exists(__options.confpath):
                print('The configuration directory or file does not exist: {}'.format(__options.confpath))
                sys.exit(1)
            __options.confpath = os.path.abspath(__options.confpath)
        # Check that the hash type for the option --hashtype is available
        if __options.hashtype and (__options.hashtype not in algorithms_guaranteed):
            print('The hash type {} you specified is not available'.format(__options.hashtype))
            sys.exit(1)
        self.__options = __options

    @property
    def options(self):
        '''Return the command line options'''
        return self.__options
