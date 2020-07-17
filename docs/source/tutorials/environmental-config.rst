Environmental Configuration
===========================

    The twelve-factor app stores config in environment variables (often shortened to env vars or env).
    Env vars are easy to change between deploys without changing any code; unlike config files,
    there is little chance of them being checked into the code repo accidentally; and unlike custom
    config files, or other config mechanisms such as Java System Properties, they are a language- and
    OS-agnostic standard. -- `The Twelve Factor App § III`_

Python has a relatively-simple way of reading environmental variables, however, things start
to get a little bit messy when reading environmental variables which must be converted
to other types, such as boolean values.

This module provides a simple way of mapping string environmental variables into common data types,
and some framework-specific types, as well as only looking for variables starting with a given
prefix.

Example Usage
-------------

We have an app, called "GDN", so to make sure we don't have conflicts with
other environmental variables set, we're going to ensure that all of our
variables are prefixed with **GDN_**.

We have 3 variables set in the environment that we want to import into our
application.

================= ===========================
 Variable          Value
================= ===========================
 GDN_DEBUG         true
 GDN_MAX_RETRIES   3
 GDN_SERVER_URL    https://my-server.digital
================= ===========================

.. code-block:: python

    from gramedia.common.env import EnvConfig

    conf = EnvConfig(app_prefix='GDN')

    # Notice the prefix is not supplied
    DEBUG = conf.boolean('DEBUG', default=False)
    MAX_RETRIES = conf.int('MAX_RETRIES', default=1)
    SERVER_URL = conf.string('SERVER_URL')


Supported Data Types
--------------------

EnvConfig.string(var_name, default=None)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Returns a string value for the given variable (identical to just calling os.getenv),
but with the addition of the automatic prefix.

EnvConfig.boolean(var_name, default=None)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Converts the environmental variable to a boolean value.  The following
values are considered True, and **ALL** other values are converted to False.

Truthy Values (all case-insensitive)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* true
* t
* yes
* y
* 1

EnvConfig.int(var_name, default=None)
^^^^^^^^^^^^^^^
Converts the specified environmental variable to an integer.

EnvConfig.django_db()
^^^^^^^^^^^^^^^^^^^^^
This is a django-specific helper method for converting a database uri string (similar to
SQLAlchemy's format), to a database configuration dictionary for use with Django.

This is so that your Dev Ops team doesn't have to 5 different variables in the environment
for a single database connection.

========== ============================================
Backend    Format
========== ============================================
Postgresql postgresql://user:password@host:port/db_name
MySQL      mysql://user:password@host:port/db_name
Oracle     oracle://user:password@host:port/db_name
SQlite     sqlite3:///some/file.sqlite3
---------- --------------------------------------------

.. _`The Twelve Factor App § III`: https://12factor.net/config
