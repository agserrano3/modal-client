# Copyright Modal Labs 2024
from typing import Optional

import typer
from rich.console import Console
from typer import Option, Typer

from modal._resolver import Resolver
from modal._utils.async_utils import synchronizer
from modal._utils.grpc_utils import retry_transient_errors
from modal.cli.utils import display_table, timestamp_to_local
from modal.client import _Client
from modal.environments import ensure_env
from modal.queue import _Queue
from modal_proto import api_pb2

queue_cli = Typer(
    name="queue",
    no_args_is_help=True,
    help="Manage `modal.Queue` objects and inspect their contents.",
)


@queue_cli.command(name="delete", rich_help_panel="Management")
@synchronizer.create_blocking
async def delete(name: str, *, yes: bool = YES_OPTION, env: Optional[str] = ENV_OPTION):
    """Delete a named Queue and all of its data."""
    # Lookup first to validate the name, even though delete is a staticmethod
    await _Queue.lookup(name, environment_name=env)
    if not yes:
        typer.confirm(
            f"Are you sure you want to irrevocably delete the modal.Queue '{name}'?",
            default=False,
            abort=True,
        )
    await _Queue.delete(name, environment_name=env)


@queue_cli.command(name="clear", rich_help_panel="Management")
@synchronizer.create_blocking
async def clear(
    name: str,
    partition: Optional[str] = PARTITION_OPTION,
    all: bool = Option(False, "-a", "--all", help="Clear the contents of all partitions."),
    yes: bool = YES_OPTION,
    *,
    env: Optional[str] = ENV_OPTION,
):
    """Clear the contents of a queue by removing all of its data."""
    q = await _Queue.lookup(name, environment_name=env)
    if not yes:
        typer.confirm(
            f"Are you sure you want to irrevocably delete the contents of modal.Queue '{name}'?",
            default=False,
            abort=True,
        )
    await q.clear(partition=partition, all=all)


@queue_cli.command(name="len", rich_help_panel="Inspection")
@synchronizer.create_blocking
async def len(
    name: str,
    partition: Optional[str] = PARTITION_OPTION,
    total: bool = Option(False, "-t", "--total", help="Compute the sum of the queue lengths across all partitions"),
    *,
    env: Optional[str] = ENV_OPTION,
):
    """Print the length of a queue partition or the total length of all partitions."""
    q = await _Queue.lookup(name, environment_name=env)
    console = Console()
    console.print(await q.len(partition=partition, total=total))
