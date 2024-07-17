# Copyright Modal Labs 2023
import importlib
import inspect
import json
import os
import warnings
from typing import NamedTuple

from synchronicity.synchronizer import FunctionWithAio

from .mdmd.mdmd import (
    Category,
    class_str,
    default_filter,
    function_str,
    module_items,
    module_str,
    object_is_private,
    package_filter,
)


class DocItem(NamedTuple):
    label: str
    category: Category
    document: str
    in_sidebar: bool = True


def validate_doc_item(docitem: DocItem) -> DocItem:
    # Check that unwanted strings aren't leaking into our docs.
    bad_strings = [
        # Presence of a to-do inside a `DocItem` usually indicates it's been
        # placed inside a function signature definition or right underneath it, before the body.
        # Fix by moving the to-do into the body or above the signature.
        "TODO:"
    ]
    for line in docitem.document.splitlines():
        for bad_str in bad_strings:
            if bad_str in line:
                msg = f"Found unwanted string '{bad_str}' in content for item '{docitem.label}'. Problem line: {line}"
                raise ValueError(msg)
    return docitem


def make_markdown_docs(items: list[DocItem], output_dir: str = None):
    def _write_file(rel_path: str, data: str):
        if output_dir is None:
            print(f"<<< {rel_path}")
            print(data)
            print(f">>> {rel_path}")
            return

        filename = os.path.join(output_dir, rel_path)
        print("Writing to", filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as fp:
            fp.write(data)

    sidebar_items = []
    for item in items:
        if item.in_sidebar:
            sidebar_items.append(
                {
                    "label": item.label,
                    "category": item.category.value,
                }
            )
        _write_file(f"{item.label}.md", item.document)

    sidebar_data = {"items": sidebar_items}
    _write_file("sidebar.json", json.dumps(sidebar_data))


if __name__ == "__main__":
    # running this module outputs docs to stdout for inspection, useful for debugging
    run(None if len(sys.argv) <= 1 else sys.argv[1])
