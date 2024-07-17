# Copyright Modal Labs 2022
import inspect
import pytest
import subprocess
import sys
import threading
import typing
from typing import Dict

import modal.partial_function
from modal import App, Cls, Function, Image, Queue, build, enter, exit, method
from modal._serialization import deserialize, serialize
from modal._utils.async_utils import synchronizer
from modal.exception import DeprecationError, ExecutionError, InvalidError, PendingDeprecationError
from modal.partial_function import (
    PartialFunction,
    _find_callables_for_obj,
    _find_partial_methods_for_user_cls,
    _PartialFunction,
    _PartialFunctionFlags,
    asgi_app,
    web_endpoint,
)
from modal.runner import deploy_app
from modal.running_app import RunningApp
from modal_proto import api_pb2

from .supports.base_class import BaseCls2

app = App("app")


@app.cls(cpu=42)
class Foo:
    @method()
    def bar(self, x: int) -> float:
        return x**3


# Reusing the app runs into an issue with stale function handles.
# TODO (akshat): have all the client tests use separate apps, and throw
# an exception if the user tries to reuse an app.
app_remote = App()


@app_remote.cls(cpu=42)
class FooRemote:
    def __init__(self, x: int, y: str) -> None:
        self.x = x
        self.y = y

    @method()
    def bar(self, z: int):
        return z**3


app_2 = App()


@app_2.cls(cpu=42)
class Bar:
    @method()
    def baz(self, x):
        return x**3


app_remote_2 = App()


@app_remote_2.cls(cpu=42)
class BarRemote:
    def __init__(self, x: int, y: str) -> None:
        self.x = x
        self.y = y

    @method()
    def baz(self, z: int):
        return z**3


app_local = App()


@app_local.cls(cpu=42, enable_memory_snapshot=True)
class FooLocal:
    def __init__(self):
        self.side_effects = ["__init__"]

    @enter(snap=True)
    def presnap(self):
        self.side_effects.append("presnap")

    @enter()
    def postsnap(self):
        self.side_effects.append("postsnap")

    @method()
    def bar(self, x):
        return x**3

    @method()
    def baz(self, y):
        return self.bar.local(y + 1)


app_remote_3 = App()


@app_remote_3.cls(cpu=42)
class NoArgRemote:
    def __init__(self) -> None:
        pass

    @method()
    def baz(self, z: int):
        return z**3


if TYPE_CHECKING:
    # Check that type annotations carry through to the decorated classes
    assert_type(Foo(), Foo)
    assert_type(Foo().bar, Function)


baz_app = App()


@baz_app.cls()
class Baz:
    def __init__(self, x):
        self.x = x

    def not_modal_method(self, y: int) -> int:
        return self.x * y


cls_with_enter_app = App()


def get_thread_id():
    return threading.current_thread().name


@cls_with_enter_app.cls()
class ClsWithEnter:
    def __init__(self, thread_id):
        self.inited = True
        self.entered = False
        self.thread_id = thread_id
        assert get_thread_id() == self.thread_id

    @enter()
    def enter(self):
        self.entered = True
        assert get_thread_id() == self.thread_id

    def not_modal_method(self, y: int) -> int:
        return y**2

    @method()
    def modal_method(self, y: int) -> int:
        return y**2


@cls_with_enter_app.cls()
class ClsWithAsyncEnter:
    def __init__(self):
        self.inited = True
        self.entered = False

    @enter()
    async def enter(self):
        self.entered = True

    @method()
    async def modal_method(self, y: int) -> int:
        return y**2


inheritance_app = App()


class BaseCls:
    @enter()
    def enter(self):
        self.x = 2

    @method()
    def run(self, y):
        return self.x * y


@inheritance_app.cls()
class DerivedCls(BaseCls):
    pass


inheritance_app_2 = App()


@inheritance_app_2.cls()
class DerivedCls2(BaseCls2):
    pass


app_unhydrated = App()


@app_unhydrated.cls()
class FooUnhydrated:
    @method()
    def bar(self):
        ...


app_method_args = App()


class ClsWithHandlers:
    @build()
    def my_build(self):
        pass

    @enter(snap=True)
    def my_memory_snapshot(self):
        pass

    @enter()
    def my_enter(self):
        pass

    @build()
    @enter()
    def my_build_and_enter(self):
        pass

    @exit()
    def my_exit(self):
        pass


web_app_app = App()


@web_app_app.cls()
class WebCls:
    @web_endpoint()
    def endpoint(self):
        pass

    @asgi_app()
    def asgi(self):
        pass


handler_app = App("handler-app")


image = Image.debian_slim().pip_install("xyz")


class HasSnapMethod:
    @enter(snap=True)
    def enter(self):
        pass

    @method()
    def f(self):
        pass


class ParameterizedClass1:
    def __init__(self, a):
        pass


class ParameterizedClass2:
    def __init__(self, a: int = 1):
        pass


class ParameterizedClass3:
    def __init__(self):
        pass
