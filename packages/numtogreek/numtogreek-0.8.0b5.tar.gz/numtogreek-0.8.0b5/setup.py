#!/usr/bin/env python3

#==================================================================================
#  Copyright:
#            
#      Copyright (C) 2012 - 2015 Konstas Marmatakis <marmako@gmail.com>
#
#   License:
#  
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License version 2 as
#      published by the Free Software Foundation.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this package; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#================================================================================== 

import sys
from distutils.core import setup

files = ['data/*']

if (sys.version_info.major, sys.version_info.minor) < (3, 3):
    print("You must have version 3.3 and above. Recommended Version: 3.4.")
    sys.exit(1)

setup(name='numtogreek',
      version=open('numtogreek/data/VERSION', encoding='utf-8').read().strip(),
      description='Converts Numbers to Greek Words',
      author='Konstas Marmatakis',
      author_email='marmako@gmail.com',
      packages=['numtogreek'],
      package_data={'numtogreek': files},
      long_description =open('numtogreek/data/README.rst', encoding='utf-8').read().strip(),
      platforms=['Linux', 'Windows'],
      classifiers=[
                   'Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Other Audience',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Natural Language :: Greek',
                   'Operating System :: Microsoft',
                   'Operating System :: Microsoft :: Windows :: Windows 7',
                   'Operating System :: POSIX',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4'])
