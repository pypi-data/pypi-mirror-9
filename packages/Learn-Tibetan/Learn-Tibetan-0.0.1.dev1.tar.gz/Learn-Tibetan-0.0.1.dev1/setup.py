#    Copyright (C) 2015 mUniKeS
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup (name = "Learn-Tibetan",
       version = "0.0.1.dev1",
       packages = find_packages(),
       scripts = ['main.py'],
       install_requires = ['pygame'],
       package_data = {},
       author="mUniKeS",
       author_email="munikes@members.fsf.org",
       description="Quiz for learn tibetan",
       license="GPL v3",
       keywords="tibetan, quiz, learn",
       url="https://budismoclasico.wordpress.com/tibetano/",
       long_description=read('README'),
       download_url="https://gitorious.org/tibetan_culture/learn_tibetan")
