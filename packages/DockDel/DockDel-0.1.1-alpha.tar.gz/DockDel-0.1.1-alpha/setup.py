# -*- coding: UTF-8 -*-

import setuptools
from distutils.core import setup

import re
VERSIONFILE='DockDel/__init__.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(
    name='DockDel',
    version=verstr,
    author='Salmon Thomas',
    author_email='ths871@gmail.com',
    packages=['DockDel'],
    url='https://github.com/tsalmon/DockDel',
    license=open('LICENSE', 'r').read(),
    description='Didel command-line tool',
    long_description=open('README.rst', 'r').read(),
    install_requires=[
        'beautifulsoup4 >= 4.3.2',
        'lxml >= 3.4.0',
        'ordereddict == 1.1',
        'requests >= 2.4.2',
    ],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    entry_points={
        'console_scripts':[
            'dockdel = dockdel.cli.run'
        ]
    },
)
