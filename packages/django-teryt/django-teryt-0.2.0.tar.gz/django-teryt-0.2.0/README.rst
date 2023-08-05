=============================
django-teryt
=============================

.. image:: https://badge.fury.io/py/django-teryt.png
    :target: http://badge.fury.io/py/django-teryt
    
.. image:: https://travis-ci.org/scibi/django-teryt.png?branch=master
        :target: https://travis-ci.org/scibi/django-teryt

.. image:: https://pypip.in/d/django-teryt/badge.png
        :target: https://crate.io/packages/django-teryt?version=latest


django-teryt is a Django app that implements TERYT database.
TERYT (Polish: "Krajowy Rejestr Urzędowy Podziału Terytorialnego Kraju",
English: "National Official Register of Territorial Division of the Country")
is a register maintained by Polish Central Statistical Office (Polish: Główny
Urząd Statystyczny; GUS). Among other things it contains:

* identifiers and names of units of territorial division,
* identifiers and names of localities,
* identifiers and names of streets

This app parses XML files from GUS and it imports them to the database.
It is meant to be used as a part of a larger system.

Documentation
-------------

The full documentation is at http://django-teryt.rtfd.org.

Quickstart
----------

Install django-teryt::

    pip install django-teryt

If you are using Django 1.6 or lower you have to install South::

    pip install 'south>=1.0'

Add ``teryt`` to ``INSTALLED_APPS`` in your ``settings.py`` and run::

    ./manage.py migrate teryt

Then download TERYT data from
`GUS website <http://www.stat.gov.pl/broker/access/prefile/listPreFiles.jspa>`_,
unpack it and then import it::

     ./manage.py teryt_parse /path/to/WMRODZ.xml /path/to/TERC.xml /path/to/SIMC.xml /path/to/ULIC.xml

Features
--------

* It can import all data from all TERYT files
* It deals with updates (just run ./manage.py teryt_parse --update TERC.xml)
* It keeps flag (aktywny) telling you if some record is still present in TERYT
  (there are some minor changes in territorial division from time to time)

Support
-------

All bug reports and pull requests are welcome. You can report them at
https://github.com/scibi/django-teryt/issues.  It can be in English
or in Polish ;)

