# Copyright Modal Labs 2022
import getpass
from typing import Optional

import typer

from modal._utils.async_utils import synchronizer
from modal.token_flow import _new_token, _set_token

token_cli = typer.Typer(name="token", help="Manage tokens.", no_args_is_help=True)
