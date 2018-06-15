Gramedia / Python Common
========================

A set of common python helper classes and functions not tied to a single framework.

Everything in here should be generic as humanly possible and should only target python 3.6.

Additionally, it is desirable to keep the dependencies to an absolute minimum.

Running Tests
-------------

.. code-block:: bash

    $ # sdist isn't strictly required -- but you probably want it anyway
    $ # in the event that you upload this to pypi.
    $ python setup.py sdist bdist_wheel
    $ pip install dist/*.whl
    $ pytest
    $ # cleanup after you're done
    $ pip uninstall gdn-python-common
    $ rm -fR .cache/ .eggs/ build/ dist/ *.egg-info

Notes
-----

* This is pretty sparse.. Please be in the habit of adding anything you like to here.
* TODO: Documentation needs added.
* TODO: create a Makefile
