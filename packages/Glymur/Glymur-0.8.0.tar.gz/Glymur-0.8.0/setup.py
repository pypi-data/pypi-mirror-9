from setuptools import setup
import os
import re
import sys

kwargs = {'name': 'Glymur',
          'description': 'Tools for accessing JPEG2000 files',
          'long_description': open('README.md').read(),
          'author': 'John Evans',
          'author_email': 'john.g.evans.ne@gmail.com',
          'url': 'https://github.com/quintusdias/glymur',
          'packages': ['glymur', 'glymur.data', 'glymur.test', 'glymur.lib',
                       'glymur.lib.test'],
          'package_data': {'glymur': ['data/*.jp2',
                                      'data/*.j2k',
                                      'data/*.jpx']},
          'entry_points': {
              'console_scripts': ['jp2dump=glymur.command_line:main'],
              },
          'license': 'MIT',
          'test_suite': 'glymur.test'}

install_requires = ['numpy>=1.7.0', 'lxml>=3.0.0']
if sys.hexversion < 0x03030000:
    install_requires.append('contextlib2>=0.4')
    install_requires.append('mock>=1.0.1')
kwargs['install_requires'] = install_requires

clssfrs = ["Programming Language :: Python",
           "Programming Language :: Python :: 2.7",
           "Programming Language :: Python :: 3.3",
           "Programming Language :: Python :: 3.4",
           "Programming Language :: Python :: Implementation :: CPython",
           "License :: OSI Approved :: MIT License",
           "Development Status :: 5 - Production/Stable",
           "Operating System :: MacOS",
           "Operating System :: POSIX :: Linux",
           "Operating System :: Microsoft :: Windows :: Windows XP",
           "Intended Audience :: Science/Research",
           "Intended Audience :: Information Technology",
           "Topic :: Software Development :: Libraries :: Python Modules"]
kwargs['classifiers'] = clssfrs

# Get the version string.  Cannot do this by importing glymur!
version_file = os.path.join('glymur', 'version.py')
with open(version_file, 'rt') as fptr:
    contents = fptr.read()
    match = re.search('version\s*=\s*"(?P<version>\d*.\d*.\d*.*)"\n', contents)
    kwargs['version'] = match.group('version')

setup(**kwargs)
