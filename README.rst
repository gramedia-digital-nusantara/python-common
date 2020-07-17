Gramedia / Python Common
========================

.. image:: https://img.shields.io/pypi/v/gdn-python-common
.. image:: https://img.shields.io/pypi/dm/gdn-python-common
.. image:: https://img.shields.io/pypi/format/gdn-python-common
.. image:: https://travis-ci.com/gramedia-digital-nusantara/python-common.svg?branch=master

A hodgepodge of common helpers and utilities used at GDN across several Python 3.6+ projects.

* Progress Bars for your long-running CLI tasks
* Configure your app from environmental variables
* Parse and Write HTTP Link Headers
* Use link-header-style pagination in Django-Rest-Framework
* Base django model classes (timestamped, name+auto slug, soft-deletable models)

Installing
----------

.. code-block:: sh

    pip install gdn-python-common

    # or, if you'd like to have django-rest-framework installed automatically
    pip install gdn-python-common[drf]
