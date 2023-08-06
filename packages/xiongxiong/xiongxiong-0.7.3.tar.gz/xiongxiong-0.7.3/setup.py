from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding = 'utf-8') as f:
  readme = f.read()

setup(
  name    = 'xiongxiong',
  version = '0.7.3',

  description      = 'Bearer token decoder',
  long_description = readme,

  url = 'https://github.com/wtsi-hgi/xiongxiong',

  license = 'AGPLv3',

  classifiers = [
    'Development Status :: 4 - Beta',
    
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    
    'Intended Audience :: Developers',
    'Topic :: Internet',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Security',
    'Topic :: Software Development :: Libraries',

    'Operating System :: OS Independent',

    'Programming Language :: JavaScript',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4'
  ],

  keywords = 'bearer token decoder authentication',

  packages = ['xiongxiong']
)
