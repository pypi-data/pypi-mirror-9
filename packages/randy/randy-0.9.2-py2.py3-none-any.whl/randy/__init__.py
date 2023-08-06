# -*- coding: utf-8 -*-
"""
Randy.
"""

__author__ = 'Francis Horsman'
__version__ = '0.9.2'
__url__ = 'https://bitbucket.org/sys-git/randy'
__email__ = 'francis.horsman@gmail.com'
__short_description__ = 'A pure-python random number generator expander'
__synopsis__ = '.\nGiven a random number generator that yields numbers in ' \
               'the range 1-n, create a new random number generator that ' \
               'yields numbers in the range 1-y where y>x, x>1, y>1, y<x**2'
__long_description__ = __short_description__ + __synopsis__

from randy.core import randy, RandyError, ParamError, MaxAttemptsError  # NOQA

if __name__ == '__main__':  # pragma no cover
    pass
