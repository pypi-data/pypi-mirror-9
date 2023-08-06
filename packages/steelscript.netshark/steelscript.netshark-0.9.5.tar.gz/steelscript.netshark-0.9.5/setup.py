# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import os
from glob import glob

try:
    from setuptools import setup, find_packages, Command
    packagedata = True
except ImportError:
    from distutils.core import setup
    from distutils.cmd import Command
    packagedata = False

    def find_packages(where='steelscript'):
        return [p for p, files, dirs in os.walk(where) if '__init__.py' in files]

from gitpy_versioning import get_version

setup_args = {
    'name':               'steelscript.netshark',
    'namespace_packages': ['steelscript'],
    'version':            get_version(),
    'author':             'Riverbed Technology',
    'author_email':       'eng-github@riverbed.com',
    'url':                'http://pythonhosted.org/steelscript',
    'license':            'MIT',
    'description':        'Python module for interacting with Riverbed NetShark with SteelScript',

    'long_description': '''SteelScript for NetShark
========================

SteelScript is a collection of libraries and scripts in Python and JavaScript for
interacting with Riverbed Technology devices.

For a complete guide to installation, see:

http://pythonhosted.org/steelscript/
    ''',

    'platforms': 'Linux, Mac OS, Windows',

    'classifiers': (
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Networking',
    ),

    'packages': find_packages(exclude=('gitpy_versioning',)),

    'data_files': (
        ('share/doc/steelscript/docs/netshark', glob('docs/*')),
        ('share/doc/steelscript/examples/netshark', glob('examples/*')),
    ),

    'scripts': (
        'utilities/shark_view_fields.py',
    ),

    'install_requires': (
        'steelscript>=0.9.5',
    ),

    'entry_points': {
        'portal.plugins': [
            'netshark = steelscript.netshark.appfwk.plugin:NetSharkPlugin'
        ],
    },
}

if packagedata:
    setup_args['include_package_data'] = True

setup(**setup_args)
