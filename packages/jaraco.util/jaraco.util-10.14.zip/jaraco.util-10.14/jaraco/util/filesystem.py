import warnings

warnings.warn("Use jaraco.path package", DeprecationWarning)

from jaraco.path import (
	encode, save_to_file, tempfile_context, replace_extension,
	ExtensionReplacer, ensure_dir_exists, read_chunks,
)
