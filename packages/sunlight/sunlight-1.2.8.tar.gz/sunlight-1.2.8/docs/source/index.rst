===============
python-sunlight
===============

Overview
========

python-sunlight provides a unified set of API clients for the various `open government data
APIs <http://services.sunlightlabs.com>`_ made available by `Sunlight Foundation <http://sunlightfoundation.com>`_
projects.

Currently this library supports the following APIs:

* `Open States API <http://openstates.org/api/>`_ (via :ref:`sunlight.openstates`)
* `Congress API <http://sunlightlabs.github.com/congress/>`_ (via :ref:`sunlight.congress`)
* `Capitol Words API <http://capitolwords.org/api/>`_ (via :ref:`sunlight.capitolwords`)

* `The old Sunlight Congress API (deprecated) <http://services.sunlightlabs.com/docs/Sunlight_Congress_API/>`_ (via :ref:`sunlight.congress_deprecated`)


Installation
============

The simplest way to install python-sunlight is via `pip <http://www.pip-installer.org/>`_::

    $ pip install sunlight

You may also wish to check the project out from `GitHub <http://github.com/sunlightlabs/python-sunlight>`_::

    $ git clone git://github.com/sunlightlabs/python-sunlight.git


Usage
=====

`Register for a Sunlight API Key <http://services.sunlightlabs.com/accounts/register/>`_ if you haven't already, then you'll be ready to start using the library.

The recommended method of providing the library with your API key is by placing your key in a file at :file:`~/.sunlight.key`.  Alternatively you can use an environment variable named :envvar:`SUNLIGHT_API_KEY` or set :data:`sunlight.config.API_KEY` within your program.

After setting your API key simply ``import sunlight`` and start using the APIs::

    >>> import sunlight
    >>> nc_legs = sunlight.openstates.legislators(state='nc')

You can also import a specific API client::

    >>> from sunlight import congress
    >>> pelosi = congress.legislators(last_name='Pelosi')[0]


For details on how to use the various APIs check out the documentation for the
individual clients:

.. toctree::
   :maxdepth: 2

   services/congress.rst
   services/openstates.rst
   services/capitolwords.rst

Extras
======

Useful utilities for working with the services.

.. toctree::
   :maxdepth: 2

   sunlight/cache.rst
   sunlight/pagination.rst

Internals
=========

Implementation details, for extending python-sunlight or more untraditional uses.

.. toctree::
   :maxdepth: 2

   sunlight/service.rst
   sunlight/config.rst
   sunlight/errors.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
