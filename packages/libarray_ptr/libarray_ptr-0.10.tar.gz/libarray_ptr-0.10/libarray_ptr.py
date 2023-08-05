# array_ptr
#
# a simple c style array ptr/size wrapper template for c++
# with stl container functionality
# and support for std::vector and boost::array
#
# Copyright (C) 2011-2013 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# array_ptr is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# array_ptr is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with array_ptr.  If not, see <http://www.gnu.org/licenses/>.

"""libarray_ptr

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['PREFIX', 'INCLUDE_PATH']

import sys
import os

from pkg_resources import parse_requirements

from path import Path


PREFIX = Path(__file__).abspath().dirname()

with PREFIX:
    __version__ = open('VERSION').read().strip()

    __requires__ = []
    with open('requirements.txt') as f:
        for req in f.readlines():
            req = req.strip()
            if req:
                __requires__.append(req)
    del f, req

    __requires__ = list(parse_requirements(__requires__))

INCLUDE_PATH = PREFIX / 'include'


def setup_keywords(dist):
    """Create data file lists and add to setup keywords.
    """
    PACKAGE = 'libarray_ptr'
    PACKAGE_DIR = Path('.')
    # Also gets the header files if building an egg
    PACKAGE_DATA = ['VERSION', 'requirements.txt']

    # Gets the header files for installing to sys.prefix
    # if doing normal build/install
    DATA_FILES = []

    if 'bdist_egg' not in sys.argv:
        PREFIX = Path(sys.prefix).abspath()
        # Store sys.prefix location (where data_files are installed)
        # as part of package_data.
        # Can later be accessed with libcarefree_objects.PREFIX
        with open('PREFIX', 'w') as f:
            f.write(PREFIX)
        PACKAGE_DATA.append('PREFIX')

    INCLUDE_FILES = []
    with Path('include'):
        for dirpath, dirnames, filenames in os.walk('.'):
            abspath = Path(dirpath).abspath()
            filepaths = []
            for fn in filenames:
                if Path(fn).ext == '.hpp':
                    filepaths.append(abspath.joinpath(fn))
            if filepaths:
                INCLUDE_FILES.append((dirpath, filepaths))

    if 'bdist_egg' not in sys.argv:
        # Install headers as data_files to sys.prefix
        for dirpath, filepaths in INCLUDE_FILES:
            DATA_FILES.append(
              (PREFIX.joinpath('include', dirpath), filepaths))
    else:
        # Install headers as package_data
        for dirpath, filepaths in INCLUDE_FILES:
            for path in filepaths:
                PACKAGE_DATA.append(PACKAGE_DIR.relpathto(path))

    dist.packages += [PACKAGE]
    dist.package_dir[PACKAGE] = PACKAGE_DIR

    dist.package_data = {PACKAGE: PACKAGE_DATA}
    dist.data_files = DATA_FILES
