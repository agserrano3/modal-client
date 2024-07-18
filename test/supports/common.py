# Copyright Modal Labs 2022
import modal

app = modal.App()


@app.function()
def f(x) -> None:
    # not actually used in test (servicer returns sum of square of all args)
    pass
