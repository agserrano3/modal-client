# Copyright Modal Labs 2023
import pytest

from modal import App, Function, Volume, web_endpoint
from modal.exception import ExecutionError, NotFoundError
from modal.runner import deploy_app


def square(x):
    # This function isn't deployed anyway
    pass
