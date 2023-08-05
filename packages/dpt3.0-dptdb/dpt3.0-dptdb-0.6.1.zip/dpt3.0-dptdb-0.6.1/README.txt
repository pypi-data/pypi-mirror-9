==========================================
DPT database API wrappers built using SWIG
==========================================

.. contents::


Description
===========

This package provides Python applications with the database API used by DPT.

DPT is a multi-user database system for Microsoft Windows.

The Python application can be as simple as a single-threaded process embedding the DPT API.

The package is available only as a source distribution.  It is built with the `MinGW`_ toolchain on Microsoft Windows, or a port of MinGW to an Operating System able to run `SWIG`_ under `Wine`_.

Setup will download the DPT API `source`_ and `documentation`_ zip files if an internet connection is available.

There is no separate documentation for Python.


Installation Instructions
=========================

Microsoft Windows
-----------------

   Build dependencies

      * `Python`_ 2.6 or later 
      * `setuptools`_
      * `SWIG`_ 2.0.8 or later
      * `MinGW Installation Manager`_

      Download and install SWIG and the MinGW Installation Manager.

      Follow the `MinGW`_ instructions to install MSYS and at least the gcc-g++ compiler suite.

      Download and install setuptools.

   Install the package by typing

       <path to>/python setup.py install

   at the command prompt of an MSYS shell with setup.py in the current directory.

   Runtime dependencies

   * Python 2.6 or later provided the version (2.6 for example) is the same as the Python used to build dptdb.
   * The MinGW runtime used to build dptdb.

Wine
----

   Build dependencies

      * `Wine`_ 
      * `Python`_ 2.6 or later 
      * `setuptools`_
      * `SWIG`_ 2.0.8 or later
      * Port of MinGW to GNU/Linux, BSDs, etc

      Download and install the port of MinGW.

      Download and install Wine.

      Download and install Microsoft Windows versions of SWIG and Python under Wine.

      Download and install setuptools in the Python installed under Wine.

   Install the package by typing

       python setup.py install

   at the command prompt of a shell with setup.py in the current directory.  You will probably need to indicate the version of Python under Wine using the PYTHON_VERSION option.  For example

       python setup.py install PYTHON_VERSION=34

   because the default, 33 at time of writing, will go out of date.

   Runtime dependencies

   * Python 2.6 or later provided the version (2.6 for example) is the same as the Python used to build dptdb.
   * The MinGW runtime used to build dptdb.


A directory named like dpt3.0_dptdb-0.5-py2.7.egg is put in site-packages by the install command.  The name means version 0.5 of dptdb for Python 2.7 wrapping version 3.0 of the DPT API.  This directory contains the dptdb and EGG-INFO directories.

The DPT documentation zip file is in the dptdb directory.


Sample code
===========

The dptdb/test directory contains a simple application which populates a database, using some contrived data, and does some simple data retrievals.

This can be run on Microsoft Windows by typing

   python pydpt-test.py

at the command prompt of a shell with pydpt-test.py in the current directory.

The equivalent command to run the sample application under Wine is

   wine python pydpt-test.py

at the command prompt of a shell with pydpt-test.py in the current directory.

You may need to use '<path to python>/python pydpt-test.py' if several versions of Python are installed.


The sample application offers seven options which create databases with different numbers of records.  Each record has 6 fields and all fields are indexed.

   One option, called normal, adds 246,625 records to a database in a 16 Mb file in about 3.33 minutes with transaction backout enabled.

   The shortest option adds 246,625 records to a database in a 16 Mb file in about 0.6 minutes with transaction backout disabled.

   The longest option adds 7,892,000 records to a database in a 526 Mb file in about 18.75 minutes with transaction backout disabled.

The figures are for a 2Gb 667MHz memory, 1.8GHz CPU, solid state drive, Microsoft Windows XP installation.


Restrictions
============

When used under Wine, very large single-step loads will fail through running out of memory because the test to decide when to complete a chunk of the load and start a new one never says 'do so'.  One workaround is to do multi-step loads, potentially a lot slower as explained in `relnotes_V2RX.html`_ from DPT_V3R0_DOCS.ZIP, which was the only way to do this before version 2 release 14 of the DPT API.  Another is to split the load into small enough chunks somehow before invoking the single-step process for each chunk.

The "Try to force 'multi-chunk' on 32Gb memory" option does enough index updating, see slowest option under `Sample code`_ for detail, to cause this failure under Wine on a 2Gb memory machine.

This is known to happen on FreeBSD.  It is possible it does not happen on other Operating Systems able to run Wine.


Notes
=====

This package is built from `DPT_V3R0_DBMS.ZIP`_, a recent DPT API source code distribution, by default.

You will need the `DPT API documentation`_ to use this package.  This is included as `DBAPI.html`_ in DPT_V3R0_DOCS.ZIP.

The DPT documentation zip file is in a directory named like C:/Python27/Lib/site-packages/dpt3.0_dptdb-0.5-py2.7.egg/dptdb, using the example at the end of `Installation Instructions`_.

The dptapi.py and _dptapi.pyd modules are built using `SWIG`_ and `MinGW`_ for a particular version of Python.  In particular a _dptapi.pyd built for Python 2.6 will work only on Python 2.6 and so on. 

The `DPT API distribution`_ contains independent scripts and instructions to build dptdb mentioning much earlier versions of the build dependencies.

This package will work only on a Python built for the Microsoft Windows platform.


.. _DPT API documentation: http://solentware.co.uk/files/DPT_V3R0_DOCS.ZIP
.. _documentation: http://solentware.co.uk/files/DPT_V3R0_DOCS.ZIP
.. _DBAPI.html: http://solentware.co.uk/files/DPT_V3R0_DOCS.ZIP
.. _relnotes_V2RX.html: http://solentware.co.uk/files/DPT_V3R0_DOCS.ZIP
.. _DPT_V3R0_DBMS.ZIP: http://solentware.co.uk/files/DPT_V3R0_DBMS.ZIP
.. _DPT API distribution: http://solentware.co.uk/files/DPT_V3R0_DBMS.ZIP
.. _source: http://solentware.co.uk/files/DPT_V3R0_DBMS.ZIP
.. _Python: https://python.org
.. _setuptools:  https://pypi.python.org/pypi/setuptools
.. _SWIG: http://swig.org
.. _MinGW: http://mingw.org
.. _Wine: https://winehq.org
.. _MinGW Installation Manager: http://sourceforge.net/projects/mingw/files/Installer/mingw-get-setup.exe/download
