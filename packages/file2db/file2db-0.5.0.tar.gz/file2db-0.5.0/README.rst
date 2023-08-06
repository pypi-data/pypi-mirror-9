===============================
File2DB
===============================

.. image:: https://img.shields.io/travis/moosejaw/file2db.svg
        :target: https://travis-ci.org/moosejaw/file2db

.. image:: https://img.shields.io/pypi/v/file2db.svg
        :target: https://pypi.python.org/pypi/file2db


Simple file to database manipulation

* Free software: GPLv3
* Documentation: https://file2db.readthedocs.org.

Commands
********

file2db info
^^^^^^^^^^^^

usage: ``file2db info [-h] [-v] (-C | -T) input_file``

positional arguments:
  ``input_file     parse data in FILE``

optional arguments:
  ``-h, --help     show this help message and exit``
  ``-v, --verbose  show debugging info``
  ``-C, --comma    comma delimited file``
  ``-T, --tab      tab delimited file``


file2db sql
^^^^^^^^^^^

usage: ``file2db sql [-h] [-v] (-C | -T) (-M | -S) [-o output_directory] -n table_name input_file``

positional arguments:
  ``input_file            parse data in FILE``

optional arguments:
  ``-h, --help            show this help message and exit``
  ``-v, --verbose         show debugging info``
  ``-C, --comma           comma delimited file``
  ``-T, --tab             tab delimited file``
  ``-M, --MySQL           to specify MySQL``
  ``-S, --SQLite          to specify SQLite``
  ``-o output_directory, --output output_directory output directory, defaults to current directory``
  ``-n table_name, --tablename table_name generate SQL DML with supplied name as the table``
