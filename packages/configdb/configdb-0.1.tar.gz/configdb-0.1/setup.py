#!/usr/bin/python
from setuptools import setup
readme = """
Quick way to store db connection details out of sources.

  import configdb
  import ooop
  ooop.OOOP( configdb.configdb(required="user pwd dbname") )

By default, attributes are taken from a YAML file at system
defined user configuration location. From the key (profile) 'default'.
If the file is not there, it is created with a yaml file
with null values. You have to fill them.

To change the profile you can use the 'profile' keyword or
`DBCONFIG_PROFILE` environ.


https://github.com/vokimon/python-configdb
"""
setup(
    name = "configdb",
    version = "0.1",
    description = "Quick way to store db connection details out of sources",
    author = "David Garcia Garzon",
    author_email = "voki@canvoki.net",
    url = 'https://github.com/vokimon/python-configdb',
    long_description = readme,
    license = 'GNU General Public License v3 or later (GPLv3+)',
    packages=[
        'configdb',
    ],
    scripts=[
    ],
    install_requires=[
        'PyYAML',
        'appdirs',
    ],
    test_suite='nose2.collector.collector',
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)

