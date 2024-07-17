# Copyright Modal Labs 2023
import pytest
import typing

import modal
from modal.client import Client
from modal.exception import ExecutionError
from modal.runner import run_app
from modal_proto import api_pb2


def dummy():
    ...
