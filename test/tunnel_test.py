# Copyright Modal Labs 2023

import pytest

from modal import forward
from modal.exception import InvalidError

from .supports.skip import skip_windows_unix_socket
