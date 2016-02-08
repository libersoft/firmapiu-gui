#!/usr/bin/python3

# Copyright (C) 2015 Libersoft srl <info[at]libersoft[dot]it
# Author Valerio Baldisserotto <svalo[at]libersoft[dot]it

#This file is part of firmapiu-gui.
#
#    firmapiu-gui is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    firmapiu-gui is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with firmapiu-gui.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
changelog = 'debian/changelog'
files=['data/icons/tango/verifica96x96.png','data/icons/tango/96px-Document-open.svg.png', 'data/icons/tango/firma96x96.png', 'data/icons/tango/impostazioni96x96.png',  'data/icons/tango/smartcardsets96x96.png', 'data/icons/tango/verifica96x96.png', 'data/icons/tango/window-close-symbolic.png','data/fpiu.svg']

setup(name = "firmapiu-gui",
	version = '0.6',
	description = "GUI for the firmapiud daemon",
	author = "Valerio Baldisserotto",
	author_email = "svalo@libersoft.it",
	url = "http://libersoft.it",
	packages = find_packages(), 
	license='GPL',
	package_data= {'data/icons/': ['data/icons/tango/*']},

	data_files=[('share/applications/',
					['data/it.libersoft.firmapiu.desktop']),
				('share/icons/hicolor/scalable/apps/',
					['data/fpiu.svg']),
				('share/icons/hicolor/192x192/apps/',
					['data/fpiu.png']),
				('share/firmapiu-gui/data/icons/tango-like',
					files)
			   ],
	long_description  = "This provides gui to firmapiud daemon. The gui should be easy-to-use"
)
