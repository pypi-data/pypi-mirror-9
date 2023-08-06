.. Bitmask documentation master file, created by
   sphinx-quickstart on Sun Jul 22 18:32:05 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bitmask
=====================================

Release v \ |version|. (`Impatient? jump to the` :ref:`Installation <install>` `section!`)

.. if you change this paragraph, change it in user/intro too
**Bitmask** is the multiplatform desktop client for the services offered by :ref:`the LEAP Platform <leapplatform>`.
It is written in python using `PySide`_ and :ref:`licensed under the GPL3 <gpl3>`.
Currently we distribute pre-compiled bundles for Linux and OSX, with Windows
bundles following soon.

.. _`PySide`: http://qt-project.org/wiki/PySide

User Guide
----------

.. toctree::
   :maxdepth: 2

   user/intro
   user/install
   user/running

Tester Guide
------------

This part of the documentation details how to fetch the last development version and how to report bugs.

.. toctree::
   :maxdepth: 1

   testers/howto

Hackers Guide
---------------

If you want to contribute to the project, we wrote this for you.

.. toctree::
   :maxdepth: 1

   dev/quickstart
   dev/environment
   dev/tests
   dev/workflow
   dev/resources
   dev/internationalization
   dev/encodings

.. dev/internals
   dev/authors
   dev/todo

Packager Guide
---------------

Docs related to the process of building and releasing a version of the client.

.. toctree::
   :maxdepth: 1

   pkg/debian
   pkg/osx
   pkg/win


Directories and Files
---------------------

Different directories and files used for the configuration of the client.

.. toctree::
   :maxdepth: 1

   config/files


API Documentation
-----------------

If you are looking for a reference to specific classes or functions, you are likely to find it here.

.. I should investigate a bit more how to skip some things, and how to give nice format
   to the docstrings.
   Maybe we should not have sphinx-apidocs building everything, but a minimal index of our own.

.. toctree::
   :maxdepth: 2

   api/leap


