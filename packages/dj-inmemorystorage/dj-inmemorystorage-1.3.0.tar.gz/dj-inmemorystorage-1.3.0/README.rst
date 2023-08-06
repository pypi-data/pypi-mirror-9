======================
dj-inmemorystorage
======================

.. image:: https://travis-ci.org/waveaccounting/dj-inmemorystorage.png?branch=master
   :target: https://travis-ci.org/waveaccounting/dj-inmemorystorage

An in-memory data storage backend for Django.

Compatible with Django's `storage API <https://docs.djangoproject.com/en/dev/ref/files/storage/>`_.

==================
Supported Versions
==================

Python 2.6/2.7 with Django 1.4+
Python 3.2/3.3/3.4 with Django 1.5+

=====
Usage
=====

In your test settings file, add

.. code:: python

    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

By default, the ``InMemoryStorage`` backend is non-persistant, meaning that
writes to it from one section of your code will not be present when reading
from another section of your code, unless both are sharing the same instance of
the storage backend.

If you need your storage to persist, you can add the following to your settings.

.. code:: python

    INMEMORYSTORAGE_PERSIST = True

===========
Differences
===========

This library is based on `django-inmemorystorage <https://github.com/codysoyland/django-inmemorystorage>`_ by Cody Soyland,
with `modifications <https://github.com/SeanHayes/django-inmemorystorage>`_ made by Seán Hayes with support for the ``url`` method,
with `additional support <https://github.com/Vostopia/django-inmemorystorage>`_ from Tore Birkeland for writing to the file.

Wave's modifications include packaging, and test modifications such that ``python setup.py test`` works. This version
also bumps the version to ``1.0.0`` and renames it to dj-inmemorystorage such that it doesn't conflict on PyPI.

The biggest difference is that this package works with Django 1.4 now (previously only 1.5+).
It also supports Python 2.6/2.7 with Django 1.4+ and Python 3.2/3.3/3.4 with Django 1.5+.

============
Contributing
============

1. Ensure that you open a pull request
2. All feature additions/bug fixes MUST include tests
