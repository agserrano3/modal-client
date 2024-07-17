# Copyright Modal Labs 2022
import asyncio
import logging
import pytest

from google.protobuf.empty_pb2 import Empty
from grpclib import GRPCError, Status

from modal import App, Dict, Image, Mount, Secret, Stub, Volume, web_endpoint
from modal.app import list_apps  # type: ignore
from modal.exception import DeprecationError, ExecutionError, InvalidError, NotFoundError
from modal.partial_function import _parse_custom_domains
from modal.runner import deploy_app, deploy_stub
from modal_proto import api_pb2

from .supports import module_1, module_2


def square(x):
    return x**2


def dummy():
    pass


async def web1(x):
    return {"square": x**2}


async def web2(x):
    return {"cube": x**3}
