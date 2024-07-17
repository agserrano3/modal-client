# Copyright Modal Labs 2024
import asyncio
import pytest

import fastapi
from starlette.requests import ClientDisconnect

from modal._asgi import asgi_app_wrapper
from modal.execution_context import _set_current_context_ids


class DummyException(Exception):
    pass


app = fastapi.FastAPI()


def _asgi_get_scope(path, method="GET"):
    return {
        "type": "http",
        "method": method,
        "path": path,
        "query_string": "",
        "headers": [],
    }


class MockIOManager:
    class get_data_in:
        @staticmethod
        async def aio(_function_call_id):
            yield {"type": "http.request", "body": b"some_body"}
            await asyncio.sleep(10)


class BrokenIOManager:
    class get_data_in:
        @staticmethod
        async def aio(_function_call_id):
            raise DummyException("error while fetching data")
            yield  # noqa (makes this a generator)


class SlowIOManager:
    class get_data_in:
        @staticmethod
        async def aio(_function_call_id):
            await asyncio.sleep(5)
            yield  # makes this an async generator


class StreamingIOManager:
    class get_data_in:
        @staticmethod
        async def aio(_function_call_id):
            yield {"type": "http.request", "body": b"foo", "more_body": True}
            yield {"type": "http.request", "body": b"bar", "more_body": True}
            yield {"type": "http.request", "body": b"baz", "more_body": False}
            yield {"type": "http.request", "body": b"this should not be read", "more_body": False}
