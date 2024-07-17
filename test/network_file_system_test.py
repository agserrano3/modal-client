# Copyright Modal Labs 2022
import pytest
import time
from io import BytesIO
from unittest import mock

import modal
from modal.exception import InvalidError, NotFoundError


def dummy():
    pass
