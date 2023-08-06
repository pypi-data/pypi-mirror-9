import warnings

warnings.warn("Use jaraco.path package", DeprecationWarning)

from jaraco.path import (
	get_unique_pathname, splitext_files_only, set_time, get_time,
	insert_before_extension, DirectoryStack, recursive_glob,
)
