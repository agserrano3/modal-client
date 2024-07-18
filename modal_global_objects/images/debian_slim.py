# Copyright Modal Labs 2022
import asyncio
import sys

from modal import App, Image


def dummy() -> None:
    pass


async def main(client=None, python_version=None) -> None:
    app = App(image=Image.debian_slim(python_version))
    app.function()(dummy)
    async with app.run.aio(client=client):
        pass


if __name__ == "__main__":
    asyncio.run(main(python_version=sys.argv[1]))
