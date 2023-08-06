#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


thisScript = os.path.abspath(sys.argv[0])
rootDir = os.path.dirname(thisScript)
moduleDir = os.path.join(rootDir, 'vmerlin')

# see http://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
main_ns = {}
versionFilePath = os.path.join(moduleDir, 'version.py')
with open(versionFilePath) as ver_file:
    exec(ver_file.read(), main_ns)

from setuptools import setup

# see https://docs.python.org/2/distutils/setupscript.html
setup(name='vmerlin',
      packages=[ 'vmerlin' ],
      version=main_ns['__version__'],
      description='vMerlin Python agent',
      long_description='vMerlin Python agent',
      author=main_ns['__author__'],
      author_email=main_ns['__email__'],
      url='https://vmerlin.cf/',
      keywords = ['application', 'performance', 'monitoring'],
      include_package_data=True,
      license='Vmware Ltd.',
      platforms='Linux, Windows, MacOS',
      # Full list: 'json', 're', 'string', 'threading', 'time', 'socket', 'traceback', 'requests'
      # Some packages are usually pre-installed so we don't list them
      install_requires=[ 'requests', 'forbiddenfruit' ],
      extras_require={
            'django':  [ "django" ],
            'mysql': [ "MySQLdb" ],
            'sqlite3': [ 'sqlite3' ],
        },
      classifiers=[ # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: Other/Proprietary License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: System :: Monitoring',
        ],
    )