from setuptools import setup, find_packages
changelog = 'debian/changelog'
files=['data/icons/tango/verifica96x96.png','data/icons/tango/96px-Document-open.svg.png', 'data/icons/tango/firma96x96.png', 'data/icons/tango/impostazioni96x96.png',  'data/icons/tango/smartcardsets96x96.png', 'data/icons/tango/verifica96x96.png', 'data/icons/tango/window-close-symbolic.png','data/fpiu.svg']

setup(name = "firmapiu-gui",
	version = '0.4',
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
				('share/firmapiu-gui',
					files)
			   ],
	long_description  = "This provides gui to firmapiud daemon. The gui should be easy-to-use"
)
