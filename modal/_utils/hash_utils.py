# Copyright Modal Labs 2022
import base64
import dataclasses
import hashlib
from typing import BinaryIO, Callable, List, Union

HASH_CHUNK_SIZE = 4096


def _update(hashers: List[Callable[[bytes], None]], data: Union[bytes, BinaryIO]) -> None:
    if isinstance(data, bytes):
        for hasher in hashers:
            hasher(data)
    else:
        assert not isinstance(data, (bytearray, memoryview))  # https://github.com/microsoft/pyright/issues/5697
        pos = data.tell()
        while True:
            chunk = data.read(HASH_CHUNK_SIZE)
            if not isinstance(chunk, bytes):
                raise ValueError(f"Only accepts bytes or byte buffer objects, not {type(chunk)} buffers")
            if not chunk:
                break
            for hasher in hashers:
                hasher(chunk)
        data.seek(pos)


@dataclasses.dataclass
class UploadHashes:
    md5_base64: str
    sha256_base64: str
