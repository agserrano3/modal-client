# Copyright Modal Labs 2024
import pytest
from pathlib import Path
from traceback import extract_tb
from typing import Dict, List, Tuple

from modal._traceback import append_modal_tb, extract_traceback, reduce_traceback_to_user_code
from modal._vendor import tblib

from .supports.raise_error import raise_error

SUPPORT_MODULE = "supports.raise_error"


def call_raise_error():
    raise_error()


def make_tb_stack(frames: List[Tuple[str, str]]) -> List[Dict]:
    """Given a minimal specification of (code filename, code name), return dict formatted for tblib."""
    tb_frames = []
    for lineno, (filename, name) in enumerate(frames):
        tb_frames.append(
            {
                "tb_lineno": lineno,
                "tb_frame": {
                    "f_lineno": lineno,
                    "f_globals": {},
                    "f_locals": {},
                    "f_code": {"co_filename": filename, "co_name": name},
                },
            }
        )
    return tb_frames


def tb_dict_from_stack_dicts(stack: List[Dict]) -> Dict:
    tb_root = tb = stack.pop(0)
    while stack:
        tb["tb_next"] = stack.pop(0)
        tb = tb["tb_next"]
    tb["tb_next"] = None
    return tb_root
