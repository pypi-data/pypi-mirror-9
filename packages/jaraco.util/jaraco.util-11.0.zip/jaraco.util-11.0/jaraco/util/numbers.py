from __future__ import unicode_literals, absolute_import


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
