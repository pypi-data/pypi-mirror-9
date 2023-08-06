=============
EEA Downloads
=============
.. image:: http://ci.eionet.europa.eu/job/eea.downloads-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.downloads-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.downloads-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.downloads-plone4/lastBuild

EEA Downloads (Media Storage) mounts a file-system directory within ZODB

Contents
========

.. contents::

Main features
=============

1. Mounts a file-system directory within ZODB

Install
=======

- Within your buildout define environment-vars per instance::

    [instance]
    environment-vars +=
      EEADOWNLOADS_NAME downloads
      EEADOWNLOADS_PATH ${buildout:directory}/var/downloads


- Make sure that registered file-system directory exists and the
  zope effective-user has read access there::

    $ mkdir -p var/downloads

- Add eea.downloads to your eggs section in your buildout and re-run buildout::

    [instance]
    eggs +=
      eea.downloads
    zcml +=
      eea.downloads

- You can download a sample buildout from
  https://github.com/eea/eea.downloads/tree/master/buildouts/plone4
- Install eea.downloads within Site Setup > Add-ons

Getting started
===============

1. Login to ZMI
2. Navigate to Plone > downloads

Storage adapter
===============
This package defines a storage interface IStorage that you can use to get
generated files system paths and Plone related URLs.
Default strategy of storing files is::

    EEADOWNLOADS_PATH / UID / MODIFIED / ID.EXTENSION

Here is an example::

    >>> from eea.downloads.interfaces import IStorage
    >>> store = IStorage(context).of('pdf')
    >>> store.filepath()
    '/opt/downloads/uid-21323e2321312/3213213/context-id.pdf'

    >>> store.absolute_url()
    'http://localhost:8080/Plone/downloads/uid-21323e2321312/3213213/context-id.pdf'

You can always provide a custom IStorage adapter for your Zope objects if you
need other file-system storage layout.

Dependencies
============

1. `Products.CMFCore`_
2. `collective.monkeypatcher`_

Source code
===========

- Latest source code (Plone 4 compatible):
  https://github.com/eea/eea.downloads


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Progress Bar (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _`collective.monkeypatcher`: http://pypi.python.org/pypi/collective.monkeypatcher
.. _`Products.CMFCore`: http://pypi.python.org/pypi/Products.CMFCore
