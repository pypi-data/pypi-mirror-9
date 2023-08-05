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

from path import path as Path

from .libarray_ptr import __version__, __requires__


# Determine the location prefix of libarray_ptr's data_files
PREFIX = Path(__path__[0])
with PREFIX:
    if Path('PREFIX').exists():
        with Path('PREFIX').open() as f:
            PREFIX = Path(f.read().strip())

INCLUDE_PATH = PREFIX / 'include'
