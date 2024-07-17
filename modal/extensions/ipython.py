# Copyright Modal Labs 2022
import atexit
import logging
import sys
from typing import Any

from modal import App
from modal._utils.async_utils import run_coro_blocking
from modal.config import config, logger

app_ctx: Any
