# Copyright Modal Labs 2022
import modal

app = modal.App("hello-world")

if not modal.is_local():
    # noqa
