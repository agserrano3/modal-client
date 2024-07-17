# Copyright Modal Labs 2022
import pytest

from modal.exception import DeprecationError

from .supports.functions import deprecated_function
try:
    deprecated_function(42)
except Exception as e:
    exc = e
finally:
    assert isinstance(exc, DeprecationError)  # If you see this, try running `pytest client/client_test`
