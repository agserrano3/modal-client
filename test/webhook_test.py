# Copyright Modal Labs 2022
import pathlib
import pytest
import subprocess
import sys

from fastapi.testclient import TestClient

from modal import App, asgi_app, web_endpoint, wsgi_app
from modal._asgi import webhook_asgi_app
from modal.exception import InvalidError
from modal.functions import Function
from modal.running_app import RunningApp
from modal_proto import api_pb2

app = App()


@app.function(cpu=42)
@web_endpoint(method="PATCH", docs=True)
async def f(x):
    return {"square": x**2}
