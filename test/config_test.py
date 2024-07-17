# Copyright Modal Labs 2022
import os
import pathlib
import pytest
import subprocess
import sys

import toml

import modal
from modal.config import Config, _lookup_workspace, config


def _cli(args, env={}):
    lib_dir = pathlib.Path(modal.__file__).parent.parent
    args = [sys.executable, "-m", "modal.cli.entry_point"] + args
    env = {
        **os.environ,
        **env,
        # For windows
        "PYTHONUTF8": "1",
    }
    ret = subprocess.run(args, cwd=lib_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = ret.stdout.decode()
    stderr = ret.stderr.decode()
    if ret.returncode != 0:
        raise Exception(f"Failed with {ret.returncode} stdout: {stdout} stderr: {stderr}")
    return stdout


def _get_config(env={}):
    stdout = _cli(["config", "show"], env=env)
    return eval(stdout)
