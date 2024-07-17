# Copyright Modal Labs 2022
import os
import platform
import subprocess
from tempfile import NamedTemporaryFile
from typing import List, Optional

import click
import typer
from rich.console import Console
from rich.syntax import Syntax

from modal._utils.async_utils import synchronizer
from modal._utils.grpc_utils import retry_transient_errors
from modal.cli.utils import display_table, timestamp_to_local
from modal.client import _Client
from modal.environments import ensure_env
from modal.secret import _Secret
from modal_proto import api_pb2

secret_cli = typer.Typer(name="secret", help="Manage secrets.", no_args_is_help=True)


def get_text_from_editor(key) -> str:
    with NamedTemporaryFile("w+", prefix="secret_buffer", suffix=".txt") as bufferfile:
        if platform.system() != "Windows":
            editor = os.getenv("EDITOR", "vi")
            input(f"Pressing enter will open an external editor ({editor}) for editing '{key}'...")
            status_code = subprocess.call([editor, bufferfile.name])
        else:
            # not tested, but according to https://stackoverflow.com/questions/1442841/lauch-default-editor-like-webbrowser-module
            # this should open an editor on Windows...
            input("Pressing enter will open an external editor to allow you to edit the secret value...")
            status_code = os.system(bufferfile.name)

        if status_code != 0:
            raise ValueError(
                "Something went wrong with the external editor. "
                "Try again, or use '--' as the value to pass input through stdin instead"
            )

        bufferfile.seek(0)
        return bufferfile.read()
