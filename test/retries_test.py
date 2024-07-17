# Copyright Modal Labs 2022
import pytest

import modal
from modal.exception import InvalidError


def default_retries_from_int():
    pass


def fixed_delay_retries():
    pass


def exponential_backoff():
    return 67


def exponential_with_max_delay():
    return 67


def dummy():
    pass


def zero_retries():
    pass
