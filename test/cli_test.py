# Copyright Modal Labs 2022-2023
import asyncio
import contextlib
import json
import os
import platform
import pytest
import re
import subprocess
import sys
import tempfile
import traceback
from pickle import dumps
from typing import List
from unittest import mock

import click
import click.testing
import toml

from modal.cli.entry_point import entrypoint_cli
from modal.exception import InvalidError
from modal_proto import api_pb2

from .supports.skip import skip_windows

dummy_app_file = """
import modal

import other_module

app = modal.App("my_app")

# Sanity check that the module is imported properly
import sys
mod = sys.modules[__name__]
assert mod.app == app
"""

dummy_other_module_file = "x = 42"


def _run(args: List[str], expected_exit_code: int = 0, expected_stderr: str = "", expected_error: str = ""):
    runner = click.testing.CliRunner(mix_stderr=False)
    with mock.patch.object(sys, "argv", args):
        res = runner.invoke(entrypoint_cli, args)
    if res.exit_code != expected_exit_code:
        print("stdout:", repr(res.stdout))
        print("stderr:", repr(res.stderr))
        traceback.print_tb(res.exc_info[2])
        print(res.exception, file=sys.stderr)
        assert res.exit_code == expected_exit_code
    if expected_stderr:
        assert re.search(expected_stderr, res.stderr), "stderr does not match expected string"
    if expected_error:
        assert re.search(expected_error, str(res.exception)), "exception message does not match expected string"
    return res





@pytest.fixture
def fresh_main_thread_assertion_module(test_dir):
    modules_to_unload = [n for n in sys.modules.keys() if "main_thread_assertion" in n]
    assert len(modules_to_unload) <= 1
    for mod in modules_to_unload:
        sys.modules.pop(mod)
    yield test_dir / "supports" / "app_run_tests" / "main_thread_assertion.py"


@pytest.fixture
def mock_shell_pty():
    def mock_get_pty_info(shell: bool) -> api_pb2.PTYInfo:
        rows, cols = (64, 128)
        return api_pb2.PTYInfo(
            enabled=True,
            winsz_rows=rows,
            winsz_cols=cols,
            env_term=os.environ.get("TERM"),
            env_colorterm=os.environ.get("COLORTERM"),
            env_term_program=os.environ.get("TERM_PROGRAM"),
            pty_type=api_pb2.PTYInfo.PTY_TYPE_SHELL,
        )

    captured_out = []
    fake_stdin = [b"echo foo\n", b"exit\n"]

    async def write_to_fd(fd: int, data: bytes):
        nonlocal captured_out
        captured_out.append((fd, data))

    @contextlib.asynccontextmanager
    async def fake_stream_from_stdin(handle_input, use_raw_terminal=False):
        async def _write():
            message_index = 0
            while True:
                if message_index == len(fake_stdin):
                    break
                data = fake_stdin[message_index]
                await handle_input(data, message_index)
                message_index += 1

        write_task = asyncio.create_task(_write())
        yield
        write_task.cancel()

    with mock.patch("rich.console.Console.is_terminal", True), mock.patch(
        "modal._pty.get_pty_info", mock_get_pty_info
    ), mock.patch("modal.runner.get_pty_info", mock_get_pty_info), mock.patch(
        "modal._utils.shell_utils.stream_from_stdin", fake_stream_from_stdin
    ), mock.patch("modal._sandbox_shell.write_to_fd", write_to_fd):
        yield fake_stdin, captured_out












