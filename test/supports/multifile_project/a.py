# Copyright Modal Labs 2024

import modal

app = modal.App()

d = modal.Dict.from_name("my-queue", create_if_missing=True)


app.include(c.app)
