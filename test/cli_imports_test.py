# Copyright Modal Labs 2023
import pytest

from modal._utils.async_utils import synchronizer
from modal.app import _App, _LocalEntrypoint
from modal.cli.import_refs import (
    DEFAULT_APP_NAME,
    get_by_object_path,
    import_file_or_module,
    parse_import_ref,
)

# Some helper vars for import_stub tests:
local_entrypoint_src = """
import modal

app = modal.App()
@app.local_entrypoint()
def main():
    pass
"""
python_module_src = """
import modal
app = modal.App("FOO")
other_app = modal.App("BAR")
@other_app.function()
def func():
    pass
@app.cls()
class Parent:
    @modal.method()
    def meth(self):
        pass

assert not __package__
"""

python_package_src = """
import modal
app = modal.App("FOO")
other_app = modal.App("BAR")
@other_app.function()
def func():
    pass
assert __package__ == "pack"
"""

python_subpackage_src = """
import modal
app = modal.App("FOO")
other_app = modal.App("BAR")
@other_app.function()
def func():
    pass
assert __package__ == "pack.sub"
"""

python_file_src = """
import modal
app = modal.App("FOO")
other_app = modal.App("BAR")
@other_app.function()
def func():
    pass

assert __package__ == ""
"""

empty_dir_with_python_file = {"mod.py": python_module_src}


dir_containing_python_package = {
    "dir": {"sub": {"mod.py": python_module_src, "subfile.py": python_file_src}},
    "pack": {
        "file.py": python_file_src,
        "mod.py": python_package_src,
        "local.py": local_entrypoint_src,
        "__init__.py": "",
        "sub": {"mod.py": python_subpackage_src, "__init__.py": "", "subfile.py": python_file_src},
    },
}
