#!python

from __future__ import (print_function, division, unicode_literals,
	absolute_import)

import collections

def mf(obj, term):
	"""
	Searches through the methods and attributes defined for obj,
	looks for those containing the term passed (case insensitive).
	Prints all matches or 'No matches' if none found.

	>>> mf('', 'SPLIT')  # doctest: +ELLIPSIS
	[...'rsplit', 'split', 'splitlines']
	"""
	methods = dir(obj)
	term = term.lower()
	result = [m for m in methods if term in m.lower()] or 'No matches'
	print(result)

def obinfo(obj):
	"""
	Print useful information about object.

	From http://www.ibm.com/developerworks/library/l-pyint.html
	"""
	if hasattr(obj, '__name__'):
		print("NAME:    ", obj.__name__)
	if hasattr(obj, '__class__'):
		print("CLASS:   ", obj.__class__.__name__)
	print("ID:      ", id(obj))
	print("TYPE:    ", type(obj))
	print("VALUE:   ", repr(obj))
	print("CALLABLE:", ['No', 'Yes'][callable(obj)])
	if hasattr(obj, '__doc__'):
		doc = getattr(obj, '__doc__')
		doc = doc.strip()
		topfive = doc.split('\n')[0:4]
		print("DOC:     ", "\n".join(topfive))
	else:
		print("No docstring. Yell at the author.")

def callable(candidate):
	# The Python 3 recommended way to do this
	return isinstance(candidate, collections.Callable)
