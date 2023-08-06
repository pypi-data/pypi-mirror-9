README
======

A pure-python random number generator expander.

Given a random number generator that yields numbers in the range 1-n,
create a new random number generator that yields numbers in the range
1-y where y>x, x>1, y>1, y>x**2

.. image:: https://codeship.com/projects/b37d0320-ae33-0132-1fd1-1a9f620f162c/status?branch=master
    :target: https://codeship.com/projects/68826
    :alt: Codeship Status
.. image:: https://api.shippable.com/projects/550718be5ab6cc13529c1947/badge?branchName=master
    :target: https://app.shippable.com/projects/550718be5ab6cc13529c1947/builds/latest
    :alt: Build Status
.. image:: https://pypip.in/download/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Downloads
.. image:: https://pypip.in/version/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Latest Version
.. image:: https://pypip.in/py_versions/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Supported Python versions
.. image:: https://pypip.in/status/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Development Status
.. image:: https://pypip.in/wheel/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Wheel Status
.. image:: https://pypip.in/egg/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Egg Status
.. image:: https://pypip.in/format/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: Download format
.. image:: https://pypip.in/license/randy/badge.svg
    :target: https://pypi.python.org/pypi/randy/
    :alt: License

How do I get set up?
~~~~~~~~~~~~~~~~~~~~

-  **python setup.py install**
-  Dependencies: **six**
-  Dependencies (test): **Coverage, nose**
-  How to run tests: **./runtests.sh**
-  Deployment instructions: **pip install shifty**

Contribution guidelines
~~~~~~~~~~~~~~~~~~~~~~~

I accept pull requests.

What about test coverage?
~~~~~~~~~~~~~~~~~~~~~~~~~

There is a full suite of unit-tests.

Who do I talk to?
~~~~~~~~~~~~~~~~~

-  Francis Horsman: **francis.horsman@gmail.com**

Example
~~~~~~~

::

    >>> from randy import randy
    >>> import random
    >>> r = randy(5, 7, fn=lambda: random.randint(1, 5))

    Slice it:
    >>> random_value = r[2] 3

    Call it:
    >>> random_value = r() 1

    Iterate with it:
    >>> random_value = iter(r).next() 5

    Print it:
    >>> str(r) 'randy(7 from 5): [[1, 2, 3, 4, 5], [6, 7, 1, 2,3], [4, 5, 6, 7, 1], [2, 3, 4, 5, 6], [7, 0, 0, 0, 0]]'



