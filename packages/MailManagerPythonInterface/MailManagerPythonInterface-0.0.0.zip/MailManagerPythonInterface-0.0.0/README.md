MailManagerPythonInterface
======
A set of utils for interfacing with mail manager

[![Build Status](http://img.shields.io/travis/KyleChamberlin/mail-manager-python-interface/master.svg)](https://travis-ci.org/KyleChamberlin/mail-manager-python-interface)
[![Coverage Status](http://img.shields.io/coveralls/KyleChamberlin/mail-manager-python-interface/master.svg)](https://coveralls.io/r/KyleChamberlin/mail-manager-python-interface)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/KyleChamberlin/mail-manager-python-interface.svg)](https://scrutinizer-ci.com/g/KyleChamberlin/mail-manager-python-interface/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/MailManagerPythonInterface.svg)](https://pypi.python.org/pypi/MailManagerPythonInterface)
[![PyPI Downloads](http://img.shields.io/pypi/dm/MailManagerPythonInterface.svg)](https://pypi.python.org/pypi/MailManagerPythonInterface)


Getting Started
===============

Requirements
------------

* Python 3.3+

Installation
------------

MailManagerPythonInterface can be installed with pip:

```
$ pip install MailManagerPythonInterface
```

or directly from the source code:

```
$ git clone https://github.com/KyleChamberlin/mail-manager-python-interface.git
$ cd mail-manager-python-interface
$ python setup.py install
```

Basic Usage
===========

After installation, the package can imported:

```
$ python
>>> import mailmanager
>>> mailmanager.__version__
```

MailManagerPythonInterface doesn't do anything, it's a template.

For Contributors
================

Requirements
------------

* Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html
* Graphviz: http://www.graphviz.org/Download.php

Installation
------------

Create a virtualenv:

```
$ make env
```

Run the tests:

```
$ make test
$ make tests  # includes integration tests
```

Build the documentation:

```
$ make doc
```

Run static analysis:

```
$ make pep8
$ make pep257
$ make pylint
$ make check  # includes all checks
```

Prepare a release:

```
$ make dist  # dry run
$ make upload
```
