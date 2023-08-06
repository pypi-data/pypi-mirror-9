#!/usr/bin/python
# .+
# .context    : task scheduling
# .title      : RunTask, coherent time task scheduler
# .kind	      : python source
# .author     : Fabrizio Pollastri
# .site	      : Torino - Italy
# .creation   :	7-Feb-2015
# .copyright  :	(c) 2013 Fabrizio Pollastri
# .license    : GNU General Public License (see below)
#
# This file is part of "RunTask, Coherent Time Task Scheduler".
#
# RunTask is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# RunTask is distributed in the hope that it will be useful,
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
import runtask
AUTHOR = re.search('([a-zA-Z]+\s+[a-zA-Z]+)\s+',runtask.__author__).group(1)
AUTHOR_EMAIL = re.search('.*?<(.*?)>',runtask.__author__).group(1)

# do setup
setup (
  name = 'runtask',
  version = runtask.__version__,
  author = AUTHOR,
  author_email = AUTHOR_EMAIL,
  maintainer = AUTHOR,
  maintainer_email = AUTHOR_EMAIL,
  url = 'http://opendcf77.inrim.it/runtask',
  download_url = 'https://testpypi.python.org/simple/runtask',
  license = 'http://www.gnu.org/licenses/gpl.txt',
  platforms = ['Linux'],
  description =  "RunTask is a coherent time task scheduler",
  long_description = """
  RunTask is a python module implementing a coherent task scheduler. The
  execution order of all controlled tasks is stricktly predictable and can
  be aligned to a given reference time. """,
  classifiers = filter(None, classifiers.split("\n")),
  py_modules = ['runtask'])

# cleanup
if os.access('MANIFEST',os.F_OK):
  os.remove('MANIFEST')

#### END
