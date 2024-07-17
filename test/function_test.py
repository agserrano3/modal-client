# Copyright Modal Labs 2022
import asyncio
import inspect
import pytest
import time
import typing
from contextlib import contextmanager

from synchronicity.exceptions import UserCodeException

import modal
from modal import App, Image, Mount, NetworkFileSystem, Proxy, web_endpoint
from modal._utils.async_utils import synchronize_api
from modal._vendor import cloudpickle
from modal.exception import ExecutionError, InvalidError
from modal.functions import Function, FunctionCall, gather
from modal.runner import deploy_app
from modal_proto import api_pb2

app = App()


if os.environ.get("GITHUB_ACTIONS") == "true":
    TIME_TOLERANCE = 0.25
else:
    TIME_TOLERANCE = 0.05


@app.function()
def foo(p, q):
    return p + q + 11  # not actually used in test (servicer returns sum of square of all args)


@app.function()
async def async_foo(p, q):
    return p + q + 12


def dummy():
    pass  # not actually used in test (servicer returns sum of square of all args)


def _pow2(x: int):
    return x**2


@contextmanager
def synchronicity_loop_delay_tracker():
    done = False

    async def _track_eventloop_blocking():
        max_dur = 0.0
        BLOCK_TIME = 0.01
        while not done:
            t0 = time.perf_counter()
            await asyncio.sleep(BLOCK_TIME)
            max_dur = max(max_dur, time.perf_counter() - t0)
        return max_dur - BLOCK_TIME  # if it takes exactly BLOCK_TIME we would have zero delay

    track_eventloop_blocking = synchronize_api(_track_eventloop_blocking)
    yield track_eventloop_blocking(_future=True)
    done = True


_side_effect_count = 0


def side_effect(_):
    global _side_effect_count
    _side_effect_count += 1


def custom_function(x):
    if x % 2 == 0:
        return x


def later():
    return "hello"


def later_gen():
    yield "foo"


async def async_later_gen():
    yield "foo"


async def slo1(sleep_seconds):
    # need to use async function body in client test to run stuff in parallel
    # but calling interface is still non-asyncio
    await asyncio.sleep(sleep_seconds)
    return sleep_seconds


class CustomException(Exception):
    pass


def failure():
    raise CustomException("foo!")


def custom_exception_function(x):
    if x == 4:
        raise CustomException("bad")
    return x * x


def import_failure():
    raise ImportError("attempted relative import with no known parent package")


lc_app = App()


@lc_app.function()
def f(x):
    return x**2


def assert_is_wrapped_dict(some_arg):
    assert type(some_arg) == modal.Dict  # this should not be a modal._Dict unwrapped instance!
    return some_arg


def assert_is_wrapped_dict_gen(some_arg):
    assert type(some_arg) == modal.Dict  # this should not be a modal._Dict unwrapped instance!
    yield some_arg


class X:
    def f(self):
        ...
