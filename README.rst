Gramedia / Python Common
========================

A set of common python helper classes and functions not tied to a single framework.

Everything in here should be generic as humanly possible and should only target python 3.6.

Additionally, it is desirable to keep the dependencies to an absolute minimum.

Running Tests
-------------

.. source-code:: bash

    $ # sdist isn't strictly required -- but you probably want it anyway
    $ # in the event that you upload this to pypi.
    $ python setup.py sdist bdist_wheel
    $ pip install dist/*.whl
    $ pytest

Notes
-----

* This is pretty sparse.. Please be in the habit of adding anything you like to here.
* Documentation needs added.

