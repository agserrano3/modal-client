# Copyright Modal Labs 2022
import os
import sys
from pathlib import Path
from typing import Optional
from click import UsageError
from grpclib import GRPCError, Status
from rich.console import Console
from rich.live import Live
from rich.syntax import Syntax
from rich.table import Table
from typer import Typer

import modal
from modal._location import display_location
from modal._output import step_completed, step_progress
from modal._utils.async_utils import synchronizer
from modal._utils.grpc_utils import retry_transient_errors
from modal.cli._download import _volume_download
from modal.cli.utils import display_table, timestamp_to_local
from modal.client import _Client
from modal.environments import ensure_env
from modal.network_file_system import _NetworkFileSystem
from modal_proto import api_pb2

nfs_cli = Typer(name="nfs", help="Read and edit `modal.NetworkFileSystem` file systems.", no_args_is_help=True)


def gen_usage_code(label):
    return f"""
@app.function(network_file_systems={{"/my_vol": modal.NetworkFileSystem.from_name("{label}")}})
def some_func():
    os.listdir("/my_vol")
"""


async def _volume_from_name(deployment_name: str) -> _NetworkFileSystem:
    network_file_system = await _NetworkFileSystem.lookup(
        deployment_name, environment_name=None
    )  # environment None will take value from config
    if not isinstance(network_file_system, _NetworkFileSystem):
        raise Exception("The specified app entity is not a network file system")
    return network_file_system
