# Copyright Modal Labs 2022
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional

from modal_proto import api_pb2


class InputStatus(IntEnum):
    """Enum representing status of a function input."""

    PENDING = 0
    SUCCESS = api_pb2.GenericResult.GENERIC_STATUS_SUCCESS
    FAILURE = api_pb2.GenericResult.GENERIC_STATUS_FAILURE
    INIT_FAILURE = api_pb2.GenericResult.GENERIC_STATUS_INIT_FAILURE
    TERMINATED = api_pb2.GenericResult.GENERIC_STATUS_TERMINATED
    TIMEOUT = api_pb2.GenericResult.GENERIC_STATUS_TIMEOUT

    @classmethod
    def _missing_(cls, value):
        return cls.PENDING


@dataclass
class InputInfo:
    """Simple data structure storing information about a function input."""

    input_id: str
    function_call_id: str
    task_id: str
    status: InputStatus
    function_name: str
    module_name: str
    children: List["InputInfo"]
