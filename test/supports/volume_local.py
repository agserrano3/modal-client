# Copyright Modal Labs 2024
from modal import App, Volume

app2 = App()


@app2.function(volumes={"/foo": Volume.from_name("my-vol")})
def volume_func() -> None:
    pass


@app2.function()
def volume_func_outer() -> None:
    volume_func.local()
