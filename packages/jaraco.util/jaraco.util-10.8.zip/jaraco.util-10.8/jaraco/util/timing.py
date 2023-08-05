import warnings
warnings.warn("jaraco.util.timing is deprecated. Use jaraco.timing instead",
	DeprecationWarning)
from jaraco.timing import Stopwatch, IntervalGovernor
