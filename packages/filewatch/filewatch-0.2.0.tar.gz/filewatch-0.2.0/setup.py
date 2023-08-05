#!/usr/bin/env python
from distutils.core import setup, Command
import os

from filewatch import VERSION

# you can also import from setuptools

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, 'README.rst'), 'rb') as fin:
    README = fin.read()

PACKAGE_NAME = 'filewatch'

tests_require = [
    'pytest',
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      cmdclass = {'test': PyTest},
      description='Python File Watcher',
      package_data={PACKAGE_NAME: ['{}.ini'.format(PACKAGE_NAME), ], },
      long_description=README,
      author='Ben Emery',
      url='https://github.com/benemery/%s' % PACKAGE_NAME,
      download_url='https://github.com/benemery/%s/tarball/%s' % (VERSION, PACKAGE_NAME),
      packages=[PACKAGE_NAME, ],
      extras_require={
        'tests': tests_require,
    },
     )