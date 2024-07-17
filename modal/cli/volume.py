# Copyright Modal Labs 2022
import os
import sys
from pathlib import Path
from typing import List, Optional

import typer
from click import UsageError
from grpclib import GRPCError, Status
from rich.console import Console
from rich.live import Live
from rich.syntax import Syntax
from typer import Typer

import modal
from modal._output import step_completed, step_progress
from modal._utils.async_utils import synchronizer
from modal._utils.grpc_utils import retry_transient_errors
from modal.cli._download import _volume_download
from modal.cli.utils import display_table, timestamp_to_local
from modal.client import _Client
from modal.environments import ensure_env
from modal.exception import deprecation_warning
from modal.volume import _Volume, _VolumeUploadContextManager
from modal_proto import api_pb2

volume_cli = Typer(
    name="volume",
    no_args_is_help=True,
    help="""
    Read and edit `modal.Volume` volumes.

    Note: users of `modal.NetworkFileSystem` should use the `modal nfs` command instead.
    """,
)


def humanize_filesize(value: int) -> str:
    if value < 0:
        raise ValueError("value should be >= 0")
    suffix = (" KiB", " MiB", " GiB", " TiB", " PiB", " EiB", " ZiB")
    format = "%.1f"
    base = 1024
    bytes_ = float(value)
    if bytes_ < base:
        return f"{bytes_:0.0f} B"
    for i, s in enumerate(suffix):
        unit = base ** (i + 2)
        if bytes_ < unit:
            break
    return format % (base * bytes_ / unit) + s


@volume_cli.command(
    name="delete",
    help="Delete a named, persistent modal.Volume.",
    rich_help_panel="Management",
)
@synchronizer.create_blocking
async def delete(
    volume_name: str = Argument(help="Name of the modal.Volume to be deleted. Case sensitive"),
    yes: bool = YES_OPTION,
    confirm: bool = Option(default=False, help="DEPRECATED: See `--yes` option"),
    env: Optional[str] = ENV_OPTION,
):
    if confirm:
        deprecation_warning(
            (2024, 4, 24),
            "The `--confirm` option is deprecated; use `--yes` to delete without prompting.",
            show_source=False,
        )
        yes = True

    if not yes:
        typer.confirm(
            f"Are you sure you want to irrevocably delete the modal.Volume '{volume_name}'?",
            default=False,
            abort=True,
        )

    await _Volume.delete(label=volume_name, environment_name=env)
