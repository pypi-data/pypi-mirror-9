# Copyright (C) 2015 Haruhiko Matsuo <halm.matsuo@gmail.com>
#
#  Distributed under the MIT License.
#  See accompanying file LICENSE.txt or copy at
#  http://opensource.org/licenses/MIT

from setuptools import setup, find_packages


setup(
    name='pyproffx',
    packages=find_packages(),
    package_data={'pyproffx': ['_lib/events.csv']},
    version='0.9.3',
    description = "A tool set of python modules for profile data analysis on Fujitsu's PRIMEHPC FX10 supercomputer",
    author='Haruhiko Matsuo',
    author_email='halm.matsuo@gmail.com',
    license='MIT',
    url='http://github.com/halm/pyproffx',
    download_url = 'https://github.com/halm/pyproffx/tarball/0.9.3',
    setup_requires=['numpy'],
    keywords=['hpc','profiler'],
)
