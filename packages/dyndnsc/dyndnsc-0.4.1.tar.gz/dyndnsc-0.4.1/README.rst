Dyndnsc - dynamic dns update client
===================================

.. image:: https://travis-ci.org/infothrill/python-dyndnsc.svg?branch=develop
    :target: https://travis-ci.org/infothrill/python-dyndnsc

.. image:: https://pypip.in/d/dyndnsc/badge.png
    :target: https://pypi.python.org/pypi/dyndnsc

.. image:: https://coveralls.io/repos/infothrill/python-dyndnsc/badge.png?branch=develop
    :target: https://coveralls.io/r/infothrill/python-dyndnsc?branch=develop 

.. image:: https://badge.fury.io/py/dyndnsc.png
    :target: http://badge.fury.io/py/dyndnsc

.. image:: https://requires.io/github/infothrill/python-dyndnsc/requirements.png?branch=develop
   :target: https://requires.io/github/infothrill/python-dyndnsc/requirements/?branch=develop
   :alt: Requirements Status

*Dyndnsc* is both a script to be used directly as well as a re-usable and
hopefully extensible python package for sending updates to dynamic
dns (ddns, dyndns) services. It is compatible with ipv4 as well as
ipv6. It ships with support for a bunch of different services and it has an
extensible configuration format that allows using foreign, but compatible
services. *Dyndnsc* ships many different IP detection mechanisms, support
for configuring multiple services in one place and it has a daemon mode for
running unattended. It has a plugin architecture for supporting notification
services like Growl or OS X Notification center.  


Quickstart / Documentation
==========================
See the Quickstart section of the http://dyndnsc.readthedocs.org/


Installation
============

.. code-block:: bash

    $ # from pypi:
    $ pip install dyndnsc

    $ # from downloaded source:
    $ python setup.py install

    $ # directly from github:
    $ pip install https://github.com/infothrill/python-dyndnsc/zipball/develop
  

Requirements
============
* Python 2.6, 2.7 or 3.2+


Status
======
*Dyndnsc* is currently still in alpha stage, which means that any interface can
still change at any time. For this to change, it shall be sufficient to have
documented use of this package which will necessitate stability (i.e.
community process).
