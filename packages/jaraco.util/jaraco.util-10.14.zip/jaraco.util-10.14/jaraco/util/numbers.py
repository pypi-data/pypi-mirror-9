from __future__ import unicode_literals, absolute_import

import warnings

import inflect


def ordinalth(n):
	"""
	Return the ordinal with 'st', 'th', or 'nd' appended as appropriate.

	>>> list(map(str, map(ordinalth, range(-5, 22))))
	['-5th', '-4th', '-3rd', '-2nd', '-1st', '0th', '1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th', '13th', '14th', '15th', '16th', '17th', '18th', '19th', '20th', '21st']
	"""
	warnings.warn("Use inflect package instead", DeprecationWarning)
	prefix = '-' if  n < 0 else ''
	return prefix + inflect.engine().ordinal(abs(n))

def coerce(value):
	"""
	coerce takes a value and attempts to convert it to a float,
	or int.

	If none of the conversions are successful, the original value is
	returned.

	>>> coerce('3')
	3

	>>> coerce('foo')
	'foo'
	"""
	result = value
	for transform in (float, int):
		try: result = transform(value)
		except ValueError: pass

	return result
