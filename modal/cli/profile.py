# Copyright Modal Labs 2022

import asyncio
import os
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from modal._utils.async_utils import synchronizer
from modal.config import Config, _lookup_workspace, _profile, config_profiles, config_set_active_profile
from modal.exception import AuthError

profile_cli = typer.Typer(name="profile", help="Switch between Modal profiles.", no_args_is_help=True)
