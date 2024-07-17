# Copyright Modal Labs 2022
import os
import pathlib
import subprocess
import sys
from typing import Tuple


def _cli(args, server_url, extra_env={}, check=True) -> Tuple[int, str, str]:
    lib_dir = pathlib.Path(__file__).parent.parent
    args = [sys.executable] + args
    env = {
        "MODAL_SERVER_URL": server_url,
        **os.environ,
        "PYTHONUTF8": "1",  # For windows
        **extra_env,
    }
    ret = subprocess.run(args, cwd=lib_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout = ret.stdout.decode()
    stderr = ret.stderr.decode()
    if check and ret.returncode != 0:
        raise Exception(f"Failed with {ret.returncode} stdout: {stdout} stderr: {stderr}")
    return ret.returncode, stdout, stderr
