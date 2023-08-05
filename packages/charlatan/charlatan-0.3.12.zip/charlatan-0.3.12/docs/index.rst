.. charlatan documentation master file, created by
   sphinx-quickstart on Wed Feb  6 11:21:22 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Charlatan's documentation!
=====================================

Charlatan is a library that lets you efficiently manage and install
fixtures.

Its features include:

- Straightforward YAML syntax to define fixtures
- Rich fixture definition functionalities, including inheritance and
  relationships (fixtures factory)
- ORM-agnostic. Tested with sqlalchemy
- Hooks to further enhance the library
- Support for Python 2 and 3

Charlatan is a library that you can use in your tests to create database
fixtures. Its aim is to provide a pragmatic interface that focuses on making it
simple to define and install fixtures for your tests. It is also agnostic in so
far as even though it's designed to work out of the box with SQLAlchemy models,
it can work with pretty much anything else.

Charlatan supports Python 2 (only tested with 2.7) and 3 (tested with 3.3).

**Why Charlatan?** Since "charlatan" used to define "an itinerant seller of
supposed remedies", we thought it would be a good name for a library providing
fixtures for tests. Credit for the name goes to Zack Heller.

Contents
--------

.. toctree::
   :maxdepth: 2

   installation
   quickstart
   file-format
   hooks
   api-reference
   contributing
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
