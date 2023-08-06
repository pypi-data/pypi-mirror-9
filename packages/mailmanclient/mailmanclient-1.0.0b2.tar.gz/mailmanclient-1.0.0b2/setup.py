# Copyright (C) 2010-2015 by the Free Software Foundation, Inc.
#
# This file is part of mailman.client.
#
# mailman.client is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# mailman.client is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mailman.client.  If not, see <http://www.gnu.org/licenses/>.

from setup_helpers import (
    description, find_doctests, get_version, long_description, require_python)
from setuptools import setup, find_packages


require_python(0x20600f0)
__version__ = get_version('src/mailmanclient/__init__.py')


setup(
    name='mailmanclient',
    version='1.0.0b2',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    maintainer='Barry Warsaw',
    maintainer_email='barry@list.org',
    description=description('README.rst'),
    long_description=long_description(
        'src/mailmanclient/README.rst',
        'src/mailmanclient/NEWS.rst'),
    license='LGPLv3',
    url='http://launchpad.net/mailman.client',
    download_url='https://launchpad.net/mailman.client/+download',
    install_requires=[
        'httplib2',
        'six',
        ],
    )
