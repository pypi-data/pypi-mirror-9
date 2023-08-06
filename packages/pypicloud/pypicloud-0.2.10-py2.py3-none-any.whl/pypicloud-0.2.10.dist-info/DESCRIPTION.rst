PyPI Cloud
==========
:Build: |build|_ |coverage|_
:Documentation: http://pypicloud.readthedocs.org/
:Downloads: http://pypi.python.org/pypi/pypicloud
:Source: https://github.com/mathcamp/pypicloud

.. |build| image:: https://travis-ci.org/mathcamp/pypicloud.png?branch=master
.. _build: https://travis-ci.org/mathcamp/pypicloud
.. |coverage| image:: https://coveralls.io/repos/mathcamp/pypicloud/badge.png?branch=master
.. _coverage: https://coveralls.io/r/mathcamp/pypicloud?branch=master

This package is a Pyramid app that runs a simple PyPI server where all the
packages are stored on Amazon's Simple Storage Service (S3).

`LIVE DEMO <http://pypi.stevearc.com>`_

Quick Start
===========
For more detailed step-by-step instructions, check out the `getting started
<http://pypicloud.readthedocs.org/en/latest/topics/getting_started.html>`_
section of the docs.

::

    virtualenv mypypi
    source mypypi/bin/activate
    pip install pypicloud waitress
    pypicloud-make-config -t server.ini
    pserve server.ini

It's running! Go to http://localhost:6543/ to view the web interface.


Changelog
=========
If you are upgrading an existing installation, read the instructions

0.2.10
------
* Bug fix: S3 download links expire incorrectly with IAM roles 
* Bug fix: ``fallback = cache`` crashes with distlib 0.2.0 

0.2.9
-----
* Bug fix: Connection problems with new S3 regions 
* Usability: Warn users trying to log in over http when ``session.secure = true`` 

0.2.8
-----
* Bug fix: Crash when migrating packages from file storage to S3 storage 

0.2.7
-----
* Bug fix: First download of package using S3 backend and ``pypi.fallback = cache`` returns 404 

0.2.6
-----
* Bug fix: Rebuilding SQL cache sometimes crashes 

0.2.5
-----
* Bug fix: Rebuilding SQL cache sometimes deadlocks 

0.2.4
-----
* Bug fix: ``ppc-migrate`` between two S3 backends 

0.2.3
-----
* Bug fix: Caching works with S3 backend 

0.2.2
-----
* Bug fix: Security bug in user auth 
* Bug fix: Package caching from pypi was slightly broken 
* Bug fix: ``ppc-migrate`` works when migrating to the same storage type 

0.2.1
-----
* Bug fix: Pre-existing S3 download links were broken by 0.2.0 

0.2.0
-----
**Upgrade breaks**: caching database

* Bug fix: Timestamp display on web interface 
* Bug fix: User registration stores password as plaintext 
* Feature: ``ppc-migrate``, command to move packages between storage backends 
* Feature: Adding support for more than one package with the same version. Now you can upload wheels! 
* Feature: Allow transparently downloading and caching packages from pypi 
* Feature: Export/Import access-control data via ``ppc-export`` and ``ppc-import`` 
* Feature: Can set default read/write permissions for packages 
* Feature: New cache backend: DynamoDB 
* Hosting all js & css ourselves (no more CDN links) 
* Obligatory miscellaneous refactoring

0.1.0
-----
* First public release


