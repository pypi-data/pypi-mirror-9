import sys
from distutils.core import setup

if sys.version_info<(3,):
	raise Exception('Sorry, only Python v3 and higher are supported')

setup(
  name = 'commanderline',
  packages = ['commanderline'], 
  version = '0.2',
  description = 'Easily expose any function to the command line',
  author = 'Tomaz Berisa',
  author_email = 'tomaz.berisa@gmail.com',
  url = 'https://bitbucket.org/tomazberisa/commanderline', 
  download_url = 'https://bitbucket.org/tomazberisa/commanderline/get/0.2.tar.gz', 
  keywords = ['command-line', 'command line', 'cli'], 
  classifiers = [],
)
