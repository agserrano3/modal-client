# Copyright Modal Labs 2022
import os
import pytest
import subprocess
import sys
from pathlib import Path

import pytest_asyncio

import modal
from modal import Mount
from modal.mount import get_auto_mounts

from . import helpers
from .supports.skip import skip_windows


@pytest.fixture
def venv_path(tmp_path, repo_root):
    venv_path = tmp_path
    subprocess.run([sys.executable, "-m", "venv", venv_path, "--copies", "--system-site-packages"], check=True)
    # Install Modal and a tiny package in the venv.
    subprocess.run([venv_path / "bin" / "python", "-m", "pip", "install", "-e", repo_root], check=True)
    subprocess.run([venv_path / "bin" / "python", "-m", "pip", "install", "--force-reinstall", "six"], check=True)
    yield venv_path


@pytest.fixture
def path_with_symlinked_files(tmp_path):
    src = tmp_path / "foo.txt"
    src.write_text("Hello")
    trg = tmp_path / "bar.txt"
    trg.symlink_to(src)
    return tmp_path, {src, trg}


script_path = "pkg_a/script.py"


@pytest_asyncio.fixture
async def env_mount_files():
    # If something is installed using pip -e, it will be bundled up as a part of the environment.
    # Those are env-specific so we ignore those as a part of the test
    filenames = []
    for mount in get_auto_mounts():
        async for file_info in mount._get_files(mount.entries):
            filenames.append(file_info.mount_filename)

    return filenames


serialized_fn_path = "pkg_a/serialized_fn.py"


@pytest.fixture
def symlinked_python_installation_venv_path(tmp_path, repo_root):
    # sets up a symlink to the python *installation* (not just the python binary)
    # and initialize the virtualenv using a path via that symlink
    # This makes the file paths of any stdlib modules use the symlinked path
    # instead of the original, which is similar to what some tools do (e.g. mise)
    # and has the potential to break automounting behavior, so we keep this
    # test as a regression test for that
    venv_path = tmp_path / "venv"
    actual_executable = Path(sys.executable).resolve()
    assert actual_executable.parent.name == "bin"
    python_install_dir = actual_executable.parent.parent
    # create a symlink to the python install *root*
    symlink_python_install = tmp_path / "python-install"
    symlink_python_install.symlink_to(python_install_dir)

    # use a python executable specified via the above symlink
    symlink_python_executable = symlink_python_install / "bin" / "python"
    # create a new venv
    subprocess.check_call([symlink_python_executable, "-m", "venv", venv_path, "--copies"])
    # check that a builtin module, like ast, is indeed identified to be in the non-resolved install path
    # since this is the source of bugs that we want to assert we don't run into!
    ast_path = subprocess.check_output(
        [venv_path / "bin" / "python", "-c", "import ast; print(ast.__file__);"], encoding="utf8"
    )
    assert ast_path != Path(ast_path).resolve()

    # install modal from current dir
    subprocess.check_call([venv_path / "bin" / "pip", "install", repo_root])
    yield venv_path


def foo():
    pass
