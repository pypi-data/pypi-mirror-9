#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:summary: Random number generator expander.

:attention: This module is re-entrant.
:author: Francis.horsman@gmail.com
"""

import collections
import threading
from six import Iterator

_CACHE = collections.defaultdict(collections.defaultdict)
_Lock = threading.Lock()


def _reset_cache():
    global _CACHE
    _CACHE = collections.defaultdict(collections.defaultdict)


class RandyError(Exception):
    """
    All expicitly raised Exceptions from randy are derived from this type.
    """
    pass


class ParamError(RandyError):
    """
    There has been an error in a parameter.
    """

    def __init__(self, *args):
        RandyError.__init__(self)


class MaxAttemptsError(RandyError, ValueError):
    """
    Max attempts (at obtaining a non-zero value from new generator) exceeded.
    """

    def __init__(self, max_attempts):
        self.max_attempts = max_attempts
        RandyError.__init__(self, max_attempts)
        ValueError.__init__(self, 'Failed to get required value ' \
                                  'after %s attempts' % self.max_attempts)

    def __str__(self):
        return ValueError.__str__(self)


class randy(Iterator):
    """
    A random number expander.
    """

    def __init__(self, size, o_size, fn=None, max_attempts=None):
        """
        Initializer.

        :type size: int, Original generator size
        :type o_size: int, Desired generator size.
        :type fn: callable, Original generator.
        :param max_attempts: Max attempts before getting a valid value.
        :raises ParamError: A parameter was incorrect.

        >>> from randy import randy
        >>> import random
        >>> r = randy(5, 7, fn=lambda: random.randint(1, 5))

        Slice it:
        >>> random_value = r[2]

        Call it:
        >>> random_value = r()

        Iterate with it (python2 example):
        >>> random_value = iter(r).next()

        Print it:
        >>> str(r)
        'randy(7 from 5): [[1, 2, 3, 4, 5], [6, 7, 1, 2, 3], [4, 5, 6, 7, 1], [2, 3, 4, 5, 6], [7, 0, 0, 0, 0]]'

        """
        size = self._validate_integer(size, 'size')
        o_size = self._validate_integer(o_size, 'o_size')

        if o_size <= size:
            raise ParamError(
                'Can only generate values greater than existing generator.')
        if o_size > (size ** 2):
            raise ParamError(
                'Can only generate values up to size:  %d' % (size ** 2))

        self._func = self._validate_random_func(fn)
        self._max_attempts = self._validate_max_attempts(max_attempts)
        self._size = size
        self._o_size = o_size
        self._init(size, o_size)

    @staticmethod
    def _validate_integer(integer, name):
        try:
            integer = int(integer)
        except (ValueError, TypeError):
            raise ParamError(
                '%s must evaluate to an integer, got: %s' % (name, integer))
        else:
            if integer < 1:
                raise ParamError('%s; must be a positive integer, got: %s.' % (
                    name, integer))
            return integer

    @property
    def max_attempts(self):
        """
        Obtain the current max_attempts value.
        """
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, max_attempts):
        """
        Set the current max_attempts value.

        :type max_attempts: int, Max attempts before getting a valid value.
        """
        self._max_attempts = self._validate_max_attempts(max_attempts)

    @staticmethod
    def _validate_max_attempts(max_attempts):
        if max_attempts:
            try:
                max_attempts = int(max_attempts)
            except:
                raise ParamError('max_Attempts must evaluate to an integer')
            else:
                if max_attempts <= 0:
                    raise ParamError(
                        'max_attempts must positive integer, '
                        'but got: %s' % max_attempts)
        return max_attempts

    @staticmethod
    def _validate_random_func(fn):
        if not callable(fn):
            raise ParamError(
                'random_func must be a callable, but got: %s' % type(fn))
        return fn

    @property
    def random_func(self):
        """
        Obtain the current Original generator.
        """
        return self._func

    @random_func.setter
    def random_func(self, func):
        """
        Set the Original generator.

        :type func: callable, Original generator.
        """
        self._func = self._validate_random_func(func)

    def _init(self, size, o_size):
        try:
            return _CACHE[size][o_size]
        except KeyError:
            with _Lock:
                try:
                    return _CACHE[size][o_size]
                except KeyError:
                    return self._create_cache_item(size, o_size)

    def __iter__(self):
        """
        Iterator method.

        This class is it's own iterator.
        """
        return self

    def __next__(self):
        """
        Iterator method.

        :return:
        """
        return self()

    def __call__(self):
        """
        Obtain the next psudo-random number in the sequence in the range:
        1 <= number <= self.size

        :return: int.
        :raises MaxAttemptsError.
        """
        value = 0
        errors = 0

        while not value and (
                    (not self._max_attempts) or (self._max_attempts and (
                            errors < self._max_attempts))):
            try:
                value = \
                    _CACHE[self._size][self._o_size][self.random_func() - 1][
                        self.random_func() - 1]
            except IndexError:  # pragma no cover
                errors += 1

        if self._max_attempts and (
                    errors == self._max_attempts):  # pragma no cover
            raise MaxAttemptsError(errors)
        return value

    def _create_cache_item(self, size, o_size):
        value = self._create(size, o_size)
        _CACHE[size][o_size] = value
        return value

    @staticmethod
    def _create(size, o_size, fill_value=0):
        return randy._chunk_iterable(
            randy._extrude_iterable(list(range(1, o_size + 1)), size,
                                    fill_value=fill_value), size)

    @staticmethod
    def _chunk_iterable(iterable, size):
        result = [iterable[i:i + size] for i in range(0, len(iterable), size)]
        return result

    @staticmethod
    def _extrude_iterable(iterable, size, fill_value=0):
        max_size = size ** 2
        remainder = divmod(max_size, len(iterable))[1]
        result = (iterable * size)[:max_size - remainder]
        remainder = max_size - len(result)
        result += [fill_value] * remainder
        return result

    def __str__(self):
        return 'randy(%d from %d): %s' % (
            self._o_size, self._size, _CACHE[self._size][self._o_size])

    def __getitem__(self, item):
        """
        Get the n'th random number from the generator.

        :param item: int, str, float (or anything that int(value) evaluates to
            an integer.
        :return: The item'th value.
        :raises ParamError: Cannot determine a non-zero positive integer
            from 'item'.
        """
        try:
            count = int(item)
        except:
            raise ParamError('Cannot get item: %s' % item)
        else:
            if count < 0:
                raise ParamError(
                    'Get value must be greater than -1')
            for _ in range(count + 1):
                value = self()
            return value
