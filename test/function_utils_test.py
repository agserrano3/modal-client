# Copyright Modal Labs 2023

from modal import method, web_endpoint
from modal._utils.function_utils import FunctionInfo, method_has_params


def hasarg(a) -> None:
    ...


def noarg() -> None:
    ...


def defaultarg(a="hello") -> None:
    ...


def wildcard_args(*wildcard_list, **wildcard_dict) -> None:
    ...


def test_is_nullary() -> None:
    assert not FunctionInfo(hasarg).is_nullary()
    assert FunctionInfo(noarg).is_nullary()
    assert FunctionInfo(defaultarg).is_nullary()
    assert FunctionInfo(wildcard_args).is_nullary()


class Cls:
    def foo(self) -> None:
        pass

    def bar(self, x) -> None:
        pass

    def buz(self, *args) -> None:
        pass


def test_method_has_params() -> None:
    assert not method_has_params(Cls.foo)
    assert not method_has_params(Cls().foo)
    assert method_has_params(Cls.bar)
    assert method_has_params(Cls().bar)
    assert method_has_params(Cls.buz)
    assert method_has_params(Cls().buz)


class Foo:
    def __init__(self) -> None:
        pass

    @method()
    def bar(self):
        return "hello"

    @web_endpoint()
    def web(self) -> None:
        pass
