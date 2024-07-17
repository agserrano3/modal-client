# Copyright Modal Labs 2022

from modal import App, Image


def dummy():
    pass


if __name__ == "__main__":
    asyncio.run(main(python_version=sys.argv[1]))
