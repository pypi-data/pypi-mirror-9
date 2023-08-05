README
######

.. image:: https://travis-ci.org/mlenzen/collections-extended.svg?branch=master
	:target: https://travis-ci.org/mlenzen/collections-extended
	:alt: Build Status


.. image:: https://coveralls.io/repos/mlenzen/collections-extended/badge.svg?branch=master
	:target: https://coveralls.io/r/mlenzen/collections-extended?branch=master
	:alt: Coverage

Documentation: http://collections-extended.lenzm.net/

GitHub: https://github.com/mlenzen/collections-extended

PyPI: https://pypi.python.org/pypi/collections-extended

Overview
========

This package includes one module - ``collections_extended``.  This
module provides a ``bag`` class,
AKA **multiset**, and a ``setlist`` class, which is a **unique list** or
**ordered set**.  There are also frozen (hashable) varieties of each included.

Tested against Python 2.6, 2.7, 3.2, 3.3, 3.4 & PyPy.

Getting Started
===============

.. code:: python

	>>> from collections_extended import bag, setlist
	>>> b = bag('abracadabra')
	>>> b.count('a')
	5
	>>> b.remove('a')
	>>> b.count('a')
	4
	>>> 'a' in b
	True
	>>> b.count('d')
	1
	>>> b.remove('d')
	>>> b.count('d')
	0
	>>> 'd' in b
	False

	>>> sl = setlist('abracadabra')
	>>> sl
	setlist(('a', 'b', 'r', 'c', 'd'))
	>>> sl[3]
	'c'
	>>> sl[-1]
	'd'
	>>> 'r' in sl  # testing for inclusion is fast
	True
	>>> sl.index('d')  # so is finding the index of an element
	4
	>>> sl.insert(1, 'd')  # inserting an element already in raises a ValueError
	Traceback (most recent call last):
	...
		raise ValueError
	ValueError
	>>> sl.index('d')
	4

Installation
============

``pip install collections-extended``

Usage
=====
	``from collections_extended import bag, frozenbag, setlist, frozensetlist``

Classes
=======
There are four new classes provided:

bags
----
bag
	This is a bag AKA multiset.
frozenbag
	This is a frozen (hashable) version of a bag.

setlists
--------
setlist
	An ordered set or a list of unique elements depending on how you look at it.
frozensetlist
	This is a frozen (hashable) version of a setlist.

Collection Factory
==================
A Collection factory is provided where you can specify whether you want the
Collection returned to be mutable, have unique elements and/or be ordered.  If
an Iterable object is passed the Collection will be filled from it, otherwise
it will be empty.

``collection(it = None, mutable=True, unique=False, ordered=False)``

:Author: Michael Lenzen
:Copyright: 2015 Michael Lenzen
:License: Apache License, Version 2.0
:Project Homepage: https://github.com/mlenzen/collections-extended
