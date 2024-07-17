# Copyright Modal Labs 2023
import importlib
import os
import pytest
import sys
from enum import IntEnum

from modal_docs.mdmd import mdmd

# Skipping a few tests on 3.7 - doesn't matter since we don't generate docs on 3.7
skip_37 = pytest.mark.skipif(sys.version_info < (3, 8), reason="Requires Python 3.8")


@skip_37
def test_module(monkeypatch):
    test_data_dir = os.path.join(os.path.dirname(__file__), "mdmd_data")
    monkeypatch.chdir(test_data_dir)
    monkeypatch.syspath_prepend(test_data_dir)
    test_module = importlib.import_module("foo")
    expected_output = open("./foo-expected.md").read()
    assert mdmd.module_str("foo", test_module) == expected_output
