# Copyright Modal Labs 2024
import asyncio
import contextlib
import errno
import os
import select
import sys
from typing import Callable, Coroutine, Optional

from modal._pty import raw_terminal, set_nonblocking
from modal.exception import ExecutionError, InteractiveTimeoutError

from .async_utils import TaskContext, asyncify


@contextlib.asynccontextmanager
async def stream_from_stdin(handle_input: Callable[[bytes, int], Coroutine], use_raw_terminal=False):
    """Stream from terminal stdin to the handle_input provided by the method"""
    quit_pipe_read, quit_pipe_write = os.pipe()

    set_nonblocking(sys.stdin.fileno())

    @asyncify
    def _read_stdin() -> Optional[bytes]:
        nonlocal quit_pipe_read
        # TODO: Windows support.
        (readable, _, _) = select.select([sys.stdin.buffer, quit_pipe_read], [], [], 5)
        if quit_pipe_read in readable:
            return None
        if sys.stdin.buffer in readable:
            return sys.stdin.buffer.read()
        # we had 5 seconds of no input. send an empty string as a "heartbeat" to the server.
        return b""

    async def _write():
        message_index = 1
        while True:
            data = await _read_stdin()
            if data is None:
                return

            await handle_input(data, message_index)

            message_index += 1

    write_task = asyncio.create_task(_write())

    if use_raw_terminal:
        with raw_terminal():
            yield
    else:
        yield
    os.write(quit_pipe_write, b"\n")
    write_task.cancel()
