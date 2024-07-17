# Copyright Modal Labs 2022

import asyncio
import time
from typing import List

from modal import (
    App,
    Sandbox,
    asgi_app,
    build,
    current_function_call_id,
    current_input_id,
    enter,
    exit,
    is_local,
    method,
    web_endpoint,
    wsgi_app,
)
from modal.exception import deprecation_warning

SLEEP_DELAY = 0.1

app = App()


@app.function()
def square(x):
    return x * x


@app.function()
def delay(t):
    time.sleep(t)
    return t


@app.function()
async def delay_async(t):
    await asyncio.sleep(t)
    return t


def stream():
    for i in range(10):
        time.sleep(SLEEP_DELAY)
        yield f"{i}..."


async def stream_async():
    for i in range(10):
        await asyncio.sleep(SLEEP_DELAY)
        yield f"{i}..."


if __name__ == "__main__":
    raise Exception("This line is not supposed to be reachable")


def gen(n):
    for i in range(n):
        yield i**2


@app.function(is_generator=True)
def fun_returning_gen(n):
    return gen(n)


@app.function()
@asgi_app()
def fastapi_app():
    from fastapi import FastAPI

    web_app = FastAPI()

    @web_app.get("/foo")
    async def foo(arg="world"):
        return {"hello": arg}

    return web_app


@app.cls()
class Cls:
    def __init__(self):
        self._k = 11

    @enter()
    def enter(self):
        self._k += 100

    @method()
    def f(self, x):
        return self._k * x

    @web_endpoint()
    def web(self, arg):
        return {"ret": arg * self._k}

    @asgi_app()
    def asgi_web(self):
        from fastapi import FastAPI

        k_at_construction = self._k  # expected to be 111
        hydrated_at_contruction = square.is_hydrated
        web_app = FastAPI()

        @web_app.get("/")
        def k(arg: str):
            return {
                "at_construction": k_at_construction,
                "at_runtime": self._k,
                "arg": arg,
                "other_hydrated": hydrated_at_contruction,
            }

        return web_app

    def _generator(self, x):
        yield x**3

    @method(is_generator=True)
    def generator(self, x):
        return self._generator(x)


@app.cls()
class ParamCls:
    def __init__(self, x: int, y: str) -> None:
        self.x = x
        self.y = y

    @method()
    def f(self, z: int):
        return f"{self.x} {self.y} {z}"

    @method()
    def g(self, z):
        return self.f.local(z)


class BaseCls:
    @enter()
    def enter(self):
        self.x = 2

    @method()
    def run(self, y):
        return self.x * y
