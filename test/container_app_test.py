# Copyright Modal Labs 2022
import json
import os
import pytest
from typing import Dict
from unittest import mock

from google.protobuf.empty_pb2 import Empty
from google.protobuf.message import Message

from modal import App, interact
from modal._container_io_manager import ContainerIOManager
from modal.running_app import RunningApp
from modal_proto import api_pb2


def my_f_1(x):
    pass
