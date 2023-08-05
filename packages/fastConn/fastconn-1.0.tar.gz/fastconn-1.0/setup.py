from distutils.core import setup
setup(name = 'fastconn',
		version = '1.0',
		author = 'Yichao Li',
		author_email = 'yichaoli.richthofen@gmail.com',
		scripts=['fa', 'fad'],
		description = 'A simple prgramme for short  communication such as share links or small files within LAN',
		install_requires=['termcolor==1.1.0'],
		dependency_links=['https://pypi.python.org/simple/termcolor/termcolor-1.1.0.tar.gz'],
		py_modules=['fa', 'fad'],)
