# Copyright Modal Labs 2024
from contextvars import ContextVar
from typing import Callable, Optional

from modal._container_io_manager import _ContainerIOManager
from modal._utils.async_utils import synchronize_api
from modal.exception import InvalidError


async def _interact() -> None:
    """Enable interactivity with user input inside a Modal container.

    See the [interactivity guide](https://modal.com/docs/guide/developing-debugging#interactivity)
    for more information on how to use this function.
    """
    container_io_manager = _ContainerIOManager._singleton
    if not container_io_manager:
        raise InvalidError("Interactivity only works inside a Modal container.")
    else:
        await container_io_manager.interact()


interact = synchronize_api(_interact)


def current_input_id() -> Optional[str]:
    """Returns the input ID for the current input.

    Can only be called from Modal function (i.e. in a container context).

    ```python
    from modal import current_input_id

    @app.function()
    def process_stuff():
        print(f"Starting to process {current_input_id()}")
    ```
    """
    try:
        return _current_input_id.get()
    except LookupError:
        return None


def _set_current_context_ids(input_id: str, function_call_id: str) -> Callable[[], None]:
    input_token = _current_input_id.set(input_id)
    function_call_token = _current_function_call_id.set(function_call_id)

    def _reset_current_context_ids():
        _current_input_id.reset(input_token)
        _current_function_call_id.reset(function_call_token)

    return _reset_current_context_ids


_current_input_id: ContextVar = ContextVar("_current_input_id")
_current_function_call_id: ContextVar = ContextVar("_current_function_call_id")
