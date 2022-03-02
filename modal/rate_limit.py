from typing import Optional

from .exception import InvalidError
from .proto import api_pb2


class RateLimit:
    """Add a rate limit to a modal function.

    # Usage

    ```python
    import modal

    # runs at most twice a second.
    @modal.function(rate_limit=modal.RateLimit(per_second=2))
    def f():
        pass

    # runs at most once a minute.
    @modal.function(rate_limit=modal.RateLimit(per_minute=1))
    def f():
        pass
    ```
    """

    def __init__(self, *, per_second: Optional[int] = None, per_minute: Optional[int] = None):
        if (per_second is None) == (per_minute is None):
            raise InvalidError("Must specify exactly one of per_second and per_minute")

        self.per_second = per_second
        self.per_minute = per_minute

    def to_proto(self) -> api_pb2.RateLimit:
        if self.per_second:
            return api_pb2.RateLimit(limit=self.per_second, interval=api_pb2.RATE_LIMIT_INTERVAL_SECOND)
        elif self.per_minute:
            return api_pb2.RateLimit(limit=self.per_minute, interval=api_pb2.RATE_LIMIT_INTERVAL_MINUTE)
        else:
            raise InvalidError("No valid protobuf definition")
