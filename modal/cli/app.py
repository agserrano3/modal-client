# Copyright Modal Labs 2022
import time
from typing import List, Optional, Union

import typer
from click import UsageError
from rich.table import Column
from rich.text import Text

from modal._utils.async_utils import synchronizer
from modal.app_utils import _list_apps
from modal.client import _Client
from modal.environments import ensure_env
from modal_proto import api_pb2

from .utils import display_table, get_app_id_from_name, stream_app_logs, timestamp_to_local

app_cli = typer.Typer(name="app", help="Manage deployed and running apps.", no_args_is_help=True)

APP_STATE_TO_MESSAGE = {
    api_pb2.APP_STATE_DEPLOYED: Text("deployed", style="green"),
    api_pb2.APP_STATE_DETACHED: Text("ephemeral (detached)", style="green"),
    api_pb2.APP_STATE_DISABLED: Text("disabled", style="dim"),
    api_pb2.APP_STATE_EPHEMERAL: Text("ephemeral", style="green"),
    api_pb2.APP_STATE_INITIALIZING: Text("initializing...", style="green"),
    api_pb2.APP_STATE_STOPPED: Text("stopped", style="blue"),
    api_pb2.APP_STATE_STOPPING: Text("stopping...", style="blue"),
}
