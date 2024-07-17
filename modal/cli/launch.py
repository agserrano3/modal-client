# Copyright Modal Labs 2023
import asyncio
import inspect
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from typer import Typer

from ..app import App
from ..exception import _CliUserExecutionError
from ..runner import run_app
from .import_refs import import_function

launch_cli = Typer(
    name="launch",
    no_args_is_help=True,
    help="""
    [Preview] Open a serverless app instance on Modal.

    This command is in preview and may change in the future.
    """,
)


def _launch_program(name: str, filename: str, args: Dict[str, Any]) -> None:
    os.environ["MODAL_LAUNCH_ARGS"] = json.dumps(args)

    program_path = str(Path(__file__).parent / "programs" / filename)
    entrypoint = import_function(program_path, "modal launch")
    app: App = entrypoint.app
    app.set_description(f"modal launch {name}")

    # `launch/` scripts must have a `local_entrypoint()` with no args, for simplicity here.
    func = entrypoint.info.raw_f
    isasync = inspect.iscoroutinefunction(func)
    with run_app(app):
        try:
            if isasync:
                asyncio.run(func())
            else:
                func()
        except Exception as exc:
            raise _CliUserExecutionError(inspect.getsourcefile(func)) from exc
