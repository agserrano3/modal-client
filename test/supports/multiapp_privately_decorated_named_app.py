# Copyright Modal Labs 2023
import modal

app = modal.App("dummy")


def foo(i):
    return 1


other_app = modal.App()
