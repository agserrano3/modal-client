# Copyright Modal Labs 2023
import pytest
import random
import string
import sys
from pathlib import Path

from watchfiles import Change

import modal
from modal._watcher import _watch_args_from_mounts
from modal.mount import Mount, _Mount


def dummy():
    pass
