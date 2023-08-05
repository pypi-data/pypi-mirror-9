#
#   Copyright 2014 Olivier Kozak
#
#   This file is part of QuickBean.
#
#   QuickBean is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General
#   Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   QuickBean is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#   details.
#
#   You should have received a copy of the GNU Lesser General Public License along with QuickBean.  If not, see
#   <http://www.gnu.org/licenses/>.
#

import os
import setuptools
import sys

sys.path.append(os.path.dirname(__file__))

import package

setuptools.setup(
    name='QuickBean',

    version=package.get_version(),

    description='A library that reduces the boilerplate code required to define beans.',
    long_description=package.load_readme_file(),

    url='https://bitbucket.org/okozak/quickbean',

    author='Olivier Kozak',
    author_email='olivier.kozak@gmail.com',

    license='GNU LGPL v3',

    packages=['quickbean'],

    install_requires=['six'],
)
