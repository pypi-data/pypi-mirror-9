# Copyright (C) 2011 Diego Pardilla Mata
#
#	This file is part of SpiderBOY.
#
# 	SpiderBOY is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from setuptools import setup, find_packages

def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup (name = "SpiderBOY",
	version = "1.0.0",
	packages = find_packages(),
	scripts = ['spiderboy.py'],
        py_modules = ['color', 'pdf', 'spinslash'],
	install_requires = ['BeautifulSoup', 'pyPdf'],
	package_data = {},
	author="Diego Pardilla",
	author_email="diegopardilla@gmail.com",
	description="A tipical crawler, returns a list of urls",
	license="GPL v3",
	keywords="crawler, spider",
        url="http://code.sidelab.es/projects/diegopardilla/wiki",
        long_description=read('README'),
	#long_description="This application returns a list of urls from a url and its level of depth.",
	download_url="git://gitorious.org/practicas_mswl/practicas_mswl_dt.git")
