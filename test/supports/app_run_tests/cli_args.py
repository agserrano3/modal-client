# Copyright Modal Labs 2022
from datetime import datetime
from typing import Optional, Union

from modal import App, method

app = App()


@app.local_entrypoint()
def dt_arg(dt: datetime) -> None:
    print(f"the day is {dt.day}")


@app.local_entrypoint()
def int_arg(i: int) -> None:
    print(repr(i), type(i))


@app.local_entrypoint()
def default_arg(i: int = 10) -> None:
    print(repr(i), type(i))


@app.local_entrypoint()
def unannotated_arg(i) -> None:
    print(repr(i), type(i))


@app.local_entrypoint()
def unannotated_default_arg(i=10) -> None:
    print(repr(i), type(i))


@app.function()
def int_arg_fn(i: int) -> None:
    print(repr(i), type(i))


@app.cls()
class ALifecycle:
    @method()
    def some_method(self, i) -> None:
        print(repr(i), type(i))

    @method()
    def some_method_int(self, i: int) -> None:
        print(repr(i), type(i))


@app.local_entrypoint()
def optional_arg(i: Optional[int] = None) -> None:
    print(repr(i), type(i))


@app.local_entrypoint()
def optional_arg_pep604(i: "int | None" = None) -> None:
    print(repr(i), type(i))


@app.local_entrypoint()
def optional_arg_postponed(i: "Optional[int]" = None) -> None:
    print(repr(i), type(i))


@app.function()
def optional_arg_fn(i: Optional[int] = None) -> None:
    print(repr(i), type(i))


@app.local_entrypoint()
def unparseable_annot(i: Union[int, str]) -> None:
    pass
