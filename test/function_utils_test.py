# Copyright Modal Labs 2023

from modal import method, web_endpoint
from modal._utils.function_utils import FunctionInfo, method_has_params


def hasarg(a):
    ...


def noarg():
    ...


def defaultarg(a="hello"):
    ...


def wildcard_args(*wildcard_list, **wildcard_dict):
    ...


class Cls:
    def foo(self):
        pass

    def bar(self, x):
        pass

    def buz(self, *args):
        pass
