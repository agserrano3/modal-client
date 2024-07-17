# Copyright Modal Labs 2022
import os
import pytest
import tempfile
from unittest import mock

from modal import App, Secret
from modal.exception import DeprecationError, InvalidError

from .supports.skip import skip_old_py


def dummy():
    ...
