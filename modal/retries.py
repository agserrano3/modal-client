from datetime import timedelta

from modal_proto import api_pb2

from .exception import InvalidError


class Retries:
    """Adds a retry policy to a Modal function.

    **Usage**

    ```python
    import modal
    stub = modal.Stub()

    # Basic configuration. This sets a policy of max 4 retries with 1-second delay between failures.
    @stub.function(retries=4)
    def f():
        pass


    # Fixed-interval retries with 3-second delay between failures.
    @stub.function(retries=modal.Retries(max_retries=2, backoff_coefficient=1.0, initial_delay=3.0))
    def g():
        pass


    # Exponential backoff, with retry delay doubling after each failure.
    @stub.function(retries=modal.Retries(max_retries=4, backoff_coefficient=2.0, initial_delay=1.0))
    def h():
        pass
    ```
    """

    def __init__(
        self,
        *,
        # The maximum number of retries that can be made in the presence of failures.
        max_retries: int,
        # Coefficent controlling how much the retry delay increases each retry attempt.
        # A backoff coefficient of 1.0 creates fixed-delay retries where the delay period will always equal the initial delay.
        backoff_coefficient: float = 2.0,
        # Number of seconds that must elapse before the first retry occurs.
        initial_delay: float = 1.0,
        # Maximum length of retry delay in seconds, preventing the delay from growing infinitely.
        max_delay: float = 60.0,
    ):
        """Construct a new function rate limit, either per-second or per-minute."""
        if max_retries < 1:
            raise InvalidError(f"Invalid retries number: {max_retries}. Function retries must be positive.")

        if max_delay < 1.0:
            raise InvalidError(f"Invalid max_delay: {max_delay}. max_delay must be at least 1 second.")

        if initial_delay < 0.0:
            raise InvalidError(f"Invalid initial_delay argument: {repr(initial_delay)}. Delay must be positive.")

        if not 1.0 <= backoff_coefficient <= 10.0:
            raise InvalidError(
                f"Invalid backoff_coefficient: {backoff_coefficient}. Coefficient must be between 1.0 (fixed-interval backoff) and 10.0"
            )

        self.max_retries = max_retries
        self.backoff_coefficient = backoff_coefficient
        self.initial_delay = timedelta(seconds=initial_delay)
        self.max_delay = timedelta(seconds=max_delay)

    def _to_proto(self) -> api_pb2.FunctionRetryPolicy:
        """Convert this retries policy to an internal protobuf representation."""
        return api_pb2.FunctionRetryPolicy(
            retries=self.max_retries,
            backoff_coefficient=self.backoff_coefficient,
            initial_delay_ms=self.initial_delay // timedelta(milliseconds=1),
            max_delay_ms=self.max_delay // timedelta(milliseconds=1),
        )
