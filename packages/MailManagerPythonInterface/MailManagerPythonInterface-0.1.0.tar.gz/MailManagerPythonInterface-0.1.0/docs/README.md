Mail Manager Python Interface
=============================

The goal of this module is to provide python users with an easy way to interact with BCC Mail
Manager on Windows. We hope to provide the following functionality:

* Import lists or Dicts into a new or existing mail manager job.
* Provide a simple YAML base configuration for the mail manager steps.
* Associate the sorted output from mail manager back to the user's program.

This project is still in the planning stage and as such is not currently usable.

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
