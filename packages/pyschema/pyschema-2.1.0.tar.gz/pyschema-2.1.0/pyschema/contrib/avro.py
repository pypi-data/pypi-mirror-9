import warnings

warnings.warn(
    "pyschema.contrib.avro is deprecated and will be removed.\n"
    "Please use the pyschema_extensions.avro package instead.",
    DeprecationWarning,
    stacklevel=2
)

from pyschema_extensions.avro import *
