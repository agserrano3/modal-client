# Copyright Modal Labs 2022
import asyncio
import logging
import os
import platform
import pytest

from synchronicity import Synchronizer

from modal._utils import async_utils
from modal._utils.async_utils import (
    TaskContext,
    queue_batch_iterator,
    retry,
    synchronize_api,
    warn_if_generator_is_not_consumed,
)

skip_github_non_linux = pytest.mark.skipif(
    (os.environ.get("GITHUB_ACTIONS") == "true" and platform.system() != "Linux"),
    reason="sleep is inaccurate on GitHub Actions runners.",
)


class SampleException(Exception):
    pass


class FailNTimes:
    def __init__(self, n_failures, exc=SampleException("Something bad happened")):
        self.n_failures = n_failures
        self.n_calls = 0
        self.exc = exc

    async def __call__(self, x):
        self.n_calls += 1
        if self.n_calls <= self.n_failures:
            raise self.exc
        else:
            return x + 1


DEBOUNCE_TIME = 0.1
