# Copyright Modal Labs 2022

import pytest
import random

from modal._utils.async_utils import synchronize_api
from modal._utils.blob_utils import (
    blob_download as _blob_download,
    blob_upload as _blob_upload,
    blob_upload_file as _blob_upload_file,
)
from modal.exception import ExecutionError

from .supports.skip import skip_old_py

blob_upload = synchronize_api(_blob_upload)
blob_download = synchronize_api(_blob_download)
blob_upload_file = synchronize_api(_blob_upload_file)
