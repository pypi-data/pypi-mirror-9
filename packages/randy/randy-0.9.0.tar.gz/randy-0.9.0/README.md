# README #

A pure-python random number generator expander.

Given a random number generator that yields numbers in the range 1-n, create a
new random number generator that yields numbers in the range 1-y where
y>x, x>1, y>1, y<x**2.

Random-number generator expanding 'like-a-boss' !

[ ![Codeship Status for sys-git/randy](https://codeship.com/projects/b37d0320-ae33-0132-1fd1-1a9f620f162c/status?branch=master)](https://codeship.com/projects/68826)
[![Build Status](https://api.shippable.com/projects/550718be5ab6cc13529c1947/badge?branchName=master)](https://app.shippable.com/projects/550718be5ab6cc13529c1947/builds/latest)

[![Downloads](https://pypip.in/download/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Latest Version](https://pypip.in/version/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Supported Python versions](https://pypip.in/py_versions/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Supported Python implementations](https://pypip.in/implementation/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Development Status](https://pypip.in/status/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Wheel Status](https://pypip.in/wheel/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Egg Status](https://pypip.in/egg/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![Download format](https://pypip.in/format/randy/badge.svg)](https://pypi.python.org/pypi/randy/)
[![License](https://pypip.in/license/randy/badge.svg)](https://pypi.python.org/pypi/randy/)


### How do I get set up? ###

* **python setup.py install**
* Dependencies: **None**
* Dependencies (test):  **Coverage, nose**
* How to run tests:  **./runtests.sh**
* Deployment instructions:  **pip install randy**

### Contribution guidelines ###
I accept pull requests.

### What about test coverage? ###
There is a full suite of unit-tests.

### Who do I talk to? ###

* Francis Horsman:  **francis.horsman@gmail.com**

### Example ###

```
>>> from randy import randy
>>> import random
>>> r = randy(5, 7, fn=lambda: random.randint(1, 5))
<class 'randy.core.randy'>

Slice it:
>>> random_value = r[2]
3

Call it:
>>> random_value = r()
1

Iterate with it:
>>> random_value = iter(r).next()
5

Print it:
>>> str(r)
'randy(7 from 5): [[1, 2, 3, 4, 5], [6, 7, 1, 2, 3], [4, 5, 6, 7, 1], [2, 3, 4, 5, 6], [7, 0, 0, 0, 0]]'
```
