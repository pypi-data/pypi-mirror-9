#!/usr/bin/env python

"""Setup script for MailManagerPythonInterface."""

import setuptools

from mailmanager import __project__, __version__

import os
if os.path.exists('README.md'):
    README = open('README.md').read()
else:
    README = ""  # a placeholder, readme is generated on release
CHANGES = open('CHANGELOG.md').read()


setuptools.setup(
    name=__project__,
    version=__version__,

    description="Mail Manager Python Interface is a Python 3 package template.",
    url='https://github.com/KyleChamberlin/mail-manager-python-interface',
    author='Kyle Chamberlin',
    author_email='KyleChamberlin@project20million.org',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': []},

    long_description=(README + '\n' + CHANGES),
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
    ],

    install_requires=open('requirements.txt').readlines(),
)
