# Copyright Modal Labs 2022
import os
import platform
import pytest
import sys


def skip_windows(msg: str):
    return pytest.mark.skipif(platform.system() == "Windows", reason=msg)
