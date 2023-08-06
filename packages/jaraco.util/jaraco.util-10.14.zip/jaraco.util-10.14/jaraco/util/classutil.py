import warnings

import jaraco.itertools
from jaraco.classes.ancestry import *

warnings.warn("Use jaraco.classes package", DeprecationWarning)

def ensure_sequence(el):
	"""
	*Deprecated*

	if item is not a sequence, return the item as a singleton in a list

	>>> ensure_sequence(3)
	[3]
	>>> ensure_sequence([3,4])
	[3, 4]
	"""
	msg = "Deprecated. Use jaraco.itertools.always_iterable"
	warnings.warn(msg, DeprecationWarning)
	return list(jaraco.itertools.always_iterable(el))

itersubclasses = iter_subclasses
