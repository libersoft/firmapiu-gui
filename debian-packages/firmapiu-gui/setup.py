from setuptools import setup, find_packages
changelog = 'debian/changelog'

setup(name = "firmapiu-gui",
	version = '0.4',
	description = "GUI for the firmapiud daemon",
	author = "Valerio Baldisserotto",
	author_email = "svalo@libersoft.it",
	url = "http://libersoft.it",
	packages = ['FirmaPiuGui'],
	license='GPL',
	data_files=[('share/applications/',
					['data/it.libersoft.firmapiu.desktop'])
				('share/icons/hicolor/scalable/apps/',
					['data/fpiu.svg'])
				('share/icons/hicolor/192x192/apps/',
					['data/fpiu.png'])
			   ],

	long_description  = "This provides gui to firmapiud daemon. The gui should be easy-to-use"
)
