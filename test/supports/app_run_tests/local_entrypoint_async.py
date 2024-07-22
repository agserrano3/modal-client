# Copyright Modal Labs 2022

import modal

app = modal.App()


@app.function()
def foo() -> None:
    pass


@app.local_entrypoint()
async def main() -> None:
    print("called locally (async)")
    await foo.remote.aio()
    await foo.remote.aio()
