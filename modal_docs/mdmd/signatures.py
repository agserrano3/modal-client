# Copyright Modal Labs 2023
import ast
import inspect
import re
import textwrap
import warnings
from typing import Tuple

from synchronicity.synchronizer import FunctionWithAio


def _signature_from_ast(func) -> Tuple[str, str]:
    """Get function signature, including decorators and comments, from source code

    Traverses functools.wraps-wrappings to get source of underlying function.

    Has the advantage over inspect.signature that it can get decorators, default arguments and comments verbatim
    from the function definition.
    """
    src = inspect.getsource(func)
    src = textwrap.dedent(src)

    def get_source_segment(src, fromline, fromcol, toline, tocol) -> str:
        lines = src.split("\n")
        lines = lines[fromline - 1 : toline]
        lines[-1] = lines[-1][:tocol]
        lines[0] = lines[0][fromcol:]
        return "\n".join(lines)

    tree = ast.parse(src)
    func_def = list(ast.iter_child_nodes(tree))[0]
    assert isinstance(func_def, (ast.FunctionDef, ast.AsyncFunctionDef))
    decorator_starts = [(item.lineno, item.col_offset - 1) for item in func_def.decorator_list]
    declaration_start = min([(func_def.lineno, func_def.col_offset)] + decorator_starts)
    body_start = min((item.lineno, item.col_offset) for item in func_def.body)

    return (
        func_def.name,
        get_source_segment(src, declaration_start[0], declaration_start[1], body_start[0], body_start[1] - 1).strip(),
    )
