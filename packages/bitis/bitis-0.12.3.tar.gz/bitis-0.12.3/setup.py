#!/usr/bin/python
# .+
# .context    : Binary Timed Signal Processing Processing Library
# .title      : Bitis distutils setup
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	21-Oct-2013
# .copyright  :	(c) 2013 Fabrizio Pollastri
# .license    : GNU General Public License (see below)
#
# This file is part of "Bitis, Binary Timed Signal Processig Library".
#
# Bitis is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Bitis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software. If not, see <http://www.gnu.org/licenses/>.
#
# .-

#from distutils.core import setup
from setuptools import setup
import os, os.path
import re
import sys

# parameters
classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: GNU General Public License (GPL)
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: POSIX :: Linux
"""

# read version string, author name, author e-mail from file
import bitis
AUTHOR = re.search('([a-zA-Z]+\s+[a-zA-Z]+)\s+',bitis.__author__).group(1)
AUTHOR_EMAIL = re.search('.*?<(.*?)>',bitis.__author__).group(1)

# do setup
setup (
  name = 'bitis',
  version = bitis.__version__,
  author = AUTHOR,
  author_email = AUTHOR_EMAIL,
  maintainer = AUTHOR,
  maintainer_email = AUTHOR_EMAIL,
  url = 'http://bitis.inrim.it',
#  download_url = 'http://bitis.inrim.it/dist/bitis-' + VERSION + '.tar.gz',
  license = 'http://www.gnu.org/licenses/gpl.txt',
  platforms = ['Linux'],
  description =  "Bitis is a processing library for binary timed signals",
  long_description = """
  Bitis is a python module that implements a full set of operators over
  binary signals represented with BTS format. The BTS format is a computer
  memory representation of a binary signal that can have a very compact
  memory footprint when the signal has a low rate of change with respect
  to its sampling period.
  """,
  classifiers = filter(None, classifiers.split("\n")),
  py_modules = ['bitis'])

# cleanup
if os.access('MANIFEST',os.F_OK):
  os.remove('MANIFEST')

#### END
