# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + tags=["parameters"]
server_addr = None
# -

from modal.client import Client
from modal_proto import api_pb2

# +
import modal

app = modal.App()


# + tags=["main"]
with client:
    with app.run(client=client, show_progress=True):
        hello.remote()
# -
