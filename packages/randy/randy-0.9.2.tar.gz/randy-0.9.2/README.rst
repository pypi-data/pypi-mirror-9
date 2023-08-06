README
======

A pure-python random number generator expander.

Given a random number generator that yields numbers in the range 1-n,
create a new random number generator that yields numbers in the range
1-y where y>x, x>1, y>1, y>> from randy import randy

>>> import random
>>> r = randy(5, 7, fn=lambda: random.randint(1, 5))

Slice it:
>>> random\_value = r[2] 3

Call it:
>>> random\_value = r() 1

Iterate with it:
>>> random\_value = iter(r).next() 5

Print it:
>>> str(r) 'randy(7 from 5): [[1, 2, 3, 4, 5], [6, 7, 1, 2,3], [4, 5, 6, 7, 1], [2, 3, 4, 5, 6], [7, 0, 0, 0, 0]]'



