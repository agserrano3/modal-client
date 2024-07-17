# Copyright Modal Labs 2022
import platform
import pytest
import subprocess
import sys

from google.protobuf.empty_pb2 import Empty

import modal.exception
from modal import Client
from modal.exception import AuthError, ConnectionError, DeprecationError, InvalidError, VersionError
from modal_proto import api_pb2

from .supports.skip import skip_windows, skip_windows_unix_socket

TEST_TIMEOUT = 4.0  # align this with the container client timeout in client.py


def client_from_env(client_addr):
    _override_config = {
        "server_url": client_addr,
        "token_id": "foo-id",
        "token_secret": "foo-secret",
        "task_id": None,
        "task_secret": None,
    }
    return Client.from_env(_override_config=_override_config)
