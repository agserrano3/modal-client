# Copyright Modal Labs 2022
import modal

app = modal.App()


@app.function()
def foo() -> None:
    print("foo")
