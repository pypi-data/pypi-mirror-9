from __future__ import unicode_literals

from jaraco import context


def throws_exception(callable, *exceptions):
	"""
	Return True if the callable throws the specified exception

	>>> throws_exception(lambda: int('3'))
	False
	>>> throws_exception(lambda: int('a'))
	True
	>>> throws_exception(lambda: int('a'), KeyError)
	False
	"""
	with context.ExceptionTrap():
		with context.ExceptionTrap(*exceptions) as exc:
			callable()
	return bool(exc)


def suppress_exception(callable, *exceptions):
	"""
	Call `callable` and return its result but suppress any specified
	exceptions (returning None).

	>>> suppress_exception(lambda: int('3'))
	3
	>>> suppress_exception(lambda: int('a'))
	>>> suppress_exception(lambda: int('a'), KeyError)
	Traceback (most recent call last):
	...
	ValueError: invalid literal for int() with base 10: 'a'
	"""
	with context.ExceptionTrap(*exceptions):
		return callable()
