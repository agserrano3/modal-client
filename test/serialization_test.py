# Copyright Modal Labs 2022
import pytest
import random

from modal import Queue
from modal._serialization import (
    deserialize,
    deserialize_data_format,
    deserialize_proto_params,
    serialize,
    serialize_data_format,
    serialize_proto_params,
)
from modal._utils.rand_pb_testing import rand_pb
from modal.exception import DeserializationError
from modal_proto import api_pb2

from .supports.skip import skip_old_py
