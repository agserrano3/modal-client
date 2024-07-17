# Copyright Modal Labs 2023
import asyncio
import pytest
import threading
import time
from unittest import mock

from modal import Function
from modal.serving import serve_app

from .supports.app_run_tests.webhook import app
from .supports.skip import skip_windows


@pytest.fixture
def app_ref(test_dir):
    return str(test_dir / "supports" / "app_run_tests" / "webhook.py")
