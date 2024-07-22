# Copyright Modal Labs 2023
import modal

app = modal.App()


@app.function()
def foo() -> None:
    pass


@app.function()
def bar() -> None:
    pass
