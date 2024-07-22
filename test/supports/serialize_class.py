# Copyright Modal Labs 2024
import sys

import modal
from modal import enter, method, web_endpoint
from modal._serialization import serialize


class UserCls:
    @enter()
    def enter(self) -> None:
        pass

    @method()
    def method(self):
        return "a"

    @web_endpoint()
    def web_endpoint(self) -> None:
        pass


app = modal.App()
app.cls()(UserCls)  # avoid warnings about not turning methods into functions

sys.stdout.buffer.write(serialize(UserCls))
