# Copyright Modal Labs 2022

import modal

app = modal.App()


@app.function()
def foo() -> None:
    pass


@app.local_entrypoint()
def main() -> None:
    print("called locally")
    foo.remote()
    foo.remote()
