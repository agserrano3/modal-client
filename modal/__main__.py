# Copyright Modal Labs 2022
import sys

from ._traceback import highlight_modal_deprecation_warnings, reduce_traceback_to_user_code, setup_rich_traceback
from .cli.entry_point import entrypoint_cli
from .cli.import_refs import _CliUserExecutionError
from .config import config


if __name__ == "__main__":
    main()
