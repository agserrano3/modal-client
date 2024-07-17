# Copyright Modal Labs 2022
import asyncio
import os
import pytest
import re
import sys
import threading
from hashlib import sha256
from tempfile import NamedTemporaryFile
from typing import List, Literal, get_args
from unittest import mock

from modal import App, Image, Mount, Secret, build, gpu, method
from modal._serialization import serialize
from modal.client import Client
from modal.exception import DeprecationError, InvalidError, VersionError
from modal.image import (
    SUPPORTED_PYTHON_SERIES,
    ImageBuilderVersion,
    _dockerhub_debian_codename,
    _dockerhub_python_version,
    _get_modal_requirements_path,
    _validate_python_version,
)
from modal.mount import PYTHON_STANDALONE_VERSIONS
from modal_proto import api_pb2

from .supports.skip import skip_windows


def dummy():
    ...


def get_image_layers(image_id: str, servicer) -> List[api_pb2.Image]:
    """Follow pointers to the previous image recursively in the servicer's list of images,
    and return a list of image layers from top to bottom."""

    result = []

    while True:
        if image_id not in servicer.images:
            break

        image = servicer.images[image_id]
        result.append(servicer.images[image_id])

        if not image.base_images:
            break

        image_id = image.base_images[0].image_id

    return result


def get_all_dockerfile_commands(image_id: str, servicer) -> str:
    layers = get_image_layers(image_id, servicer)
    return "\n".join([cmd for layer in layers for cmd in layer.dockerfile_commands])


@pytest.fixture(params=get_args(ImageBuilderVersion))
def builder_version(request, server_url_env, modal_config):
    version = request.param
    with modal_config():
        with mock.patch("test.conftest.ImageBuilderVersion", Literal[version]):  # type: ignore
            yield version


def run_f():
    print("foo!")


VARIABLE_1 = 1
VARIABLE_2 = 3


def run_f_globals():
    print("foo!", VARIABLE_1)


VARIABLE_3 = threading.Lock()
VARIABLE_4 = "bar"


def run_f_unserializable_globals():
    print("foo!", VARIABLE_3, VARIABLE_4)


def run_f_with_args(arg, *, kwarg):
    print("building!", arg, kwarg)


@pytest.fixture
def tmp_path_with_content(tmp_path):
    (tmp_path / "data.txt").write_text("hello")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "sub").write_text("world")
    return tmp_path


cls_app = App()

VARIABLE_5 = 1
VARIABLE_6 = 1


class FooInstance:
    not_used_by_build_method: str = "normal"
    used_by_build_method: str = "normal"

    @build()
    def build_func(self):
        global VARIABLE_5

        print("global variable", VARIABLE_5)
        print("static class var", FooInstance.used_by_build_method)
        FooInstance.used_by_build_method = "normal"


parallel_app = App()
