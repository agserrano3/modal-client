# Copyright Modal Labs 2023
import asyncio
import io
import os
import platform
import pytest
import re
import sys
import time
from pathlib import Path
from unittest import mock

import modal
from modal.exception import DeprecationError, InvalidError, NotFoundError, VolumeUploadTimeoutError
from modal.volume import _open_files_error_annotation
from modal_proto import api_pb2


def dummy():
    pass
