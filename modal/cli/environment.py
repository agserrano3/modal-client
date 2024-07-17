# Copyright Modal Labs 2023
from typing import Optional

import typer
from click import UsageError
from grpclib import GRPCError, Status
from typing_extensions import Annotated

from modal import environments
from modal._utils.name_utils import check_environment_name
from modal.cli.utils import display_table
from modal.config import config
from modal.exception import InvalidError

ENVIRONMENT_HELP_TEXT = """Create and interact with Environments

Environments are sub-divisons of workspaces, allowing you to deploy the same app
in different namespaces. Each environment has their own set of Secrets and any
lookups performed from an app in an environment will by default look for entities
in the same environment.

Typical use cases for environments include having one for development and one for
production, to prevent overwriting production apps when developing new features
while still being able to deploy changes to a live environment.
"""

environment_cli = typer.Typer(name="environment", help=ENVIRONMENT_HELP_TEXT, no_args_is_help=True)


class RenderableBool:
    def __init__(self, value: bool):
        self.value = value

    def __rich__(self):
        return repr(self.value)


ENVIRONMENT_CREATE_HELP = """Create a new environment in the current workspace"""


ENVIRONMENT_DELETE_HELP = """Delete an environment in the current workspace

Deletes all apps in the selected environment and deletes the environment irrevocably.
"""


ENVIRONMENT_UPDATE_HELP = """Update the name or web suffix of an environment"""
