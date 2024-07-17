# Copyright Modal Labs 2022
import modal

app = modal.App()


# This should fail in a container
with app.run():
    print(square.remote(42))
