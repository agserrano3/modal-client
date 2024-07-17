# Copyright Modal Labs 2022
import contextlib
import os
import sys
from typing import Optional, Tuple

from modal_proto import api_pb2


def get_winsz(fd) -> Tuple[Optional[int], Optional[int]]:
    try:
        import fcntl
        import struct
        import termios

        return struct.unpack("hh", fcntl.ioctl(fd, termios.TIOCGWINSZ, "1234"))  # type: ignore
    except Exception:
        return None, None


def set_nonblocking(fd: int):
    import fcntl

    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)


@contextlib.contextmanager
def raw_terminal():
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd, termios.TCSADRAIN)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
