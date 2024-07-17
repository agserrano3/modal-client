# Copyright Modal Labs 2022
import asyncio
import hashlib
import io
import pytest

from modal._utils.blob_utils import BytesIOSegmentPayload
from modal._utils.name_utils import (
    check_object_name,
    is_valid_environment_name,
    is_valid_object_name,
    is_valid_subdomain_label,
    is_valid_tag,
)
from modal._utils.package_utils import parse_major_minor_version
from modal.exception import DeprecationError, InvalidError
