Mail Manager Python Interface
=============================
A set of utils for interfacing with [BCC Mail Manager](http://www.bccsoftware.com/bcc-mail-manager)

The goal of this module is to provide python users with an easy way to interact with BCC Mail
Manager on [Windows](https://microsoft.com/windows/). We hope to provide the following functionality:

* Import lists or Dicts into a new or existing mail manager job.
* Provide a simple YAML base configuration for the mail manager steps.
* Associate the sorted output from mail manager back to the user's program.

This project is still in the planning stage and as such is not currently usable.

[![Build Status](http://img.shields.io/travis/KyleChamberlin/mail-manager-python-interface/master.svg)](https://travis-ci.org/KyleChamberlin/mail-manager-python-interface)
[![Coverage Status](http://img.shields.io/coveralls/KyleChamberlin/mail-manager-python-interface/master.svg)](https://coveralls.io/r/KyleChamberlin/mail-manager-python-interface)
[![Scrutinizer Code Quality](http://img.shields.io/scrutinizer/g/KyleChamberlin/mail-manager-python-interface.svg)](https://scrutinizer-ci.com/g/KyleChamberlin/mail-manager-python-interface/?branch=master)
[![PyPI Version](http://img.shields.io/pypi/v/MailManagerPythonInterface.svg)](https://pypi.python.org/pypi/MailManagerPythonInterface)
[![PyPI Downloads](http://img.shields.io/pypi/dm/MailManagerPythonInterface.svg)](https://pypi.python.org/pypi/MailManagerPythonInterface)
[![Documentation Status](https://readthedocs.org/projects/mail-manager-python-interface/badge/?version=latest)](https://readthedocs.org/projects/mail-manager-python-interface/?badge=latest)

Getting Started
===============


Requirements
------------

* Python 3.4+

Installation
------------

Mail Manager Python Interface can be installed with pip:


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

For Contributors
================

Be sure to read the [[CONTRIBUTING.md]] document in this repository for further information about how to contribute to this project.

Before you contribute you will also need to sign our [Contributor License Agreement](CLA.md) which is [hosted on CLAHub](https://www.clahub.com/agreements/KyleChamberlin/mail-manager-python-interface).

Requirements
------------

* Make:
    * Windows: http://cygwin.com/install.html
    * Mac: https://developer.apple.com/xcode
    * Linux: http://www.gnu.org/software/make (likely already installed)
* virtualenv: https://pypi.python.org/pypi/virtualenv#installation
* Pandoc: http://johnmacfarlane.net/pandoc/installing.html

Installation
------------

#### Create a virtualenv:

```
$ make env
```

#### Run the tests:

```
$ make test
$ make tests  # includes integration tests
```

#### Build the documentation:

```
$ make doc
```

#### Run static analysis:

```
$ make pep8
$ make pep257
$ make pylint
$ make check  # includes all checks
```

#### Prepare a release:

```
$ make dist  # dry run
$ make upload
```

Copyright
---------

Copyright 2015 Kyle Chamberlin

License
-------

*Licensed under the __Apache License__, Version __2.0__ (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at*

[Apache.org - Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

*Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an __"AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND__, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.*
