# Copyright Modal Labs 2022
import pprint

import typer

from modal.config import _profile, _store_user_config, config

config_cli = typer.Typer(
    name="config",
    help="""
    Manage client configuration for the current profile.

    Refer to https://modal.com/docs/reference/modal.config for a full explanation
    of what these options mean, and how to set them.
    """,
    no_args_is_help=True,
)


SET_DEFAULT_ENV_HELP = """Set the default Modal environment for the active profile

The default environment of a profile is used when no --env flag is passed to `modal run`, `modal deploy` etc.

If no default environment is set, and there exists multiple environments in a workspace, an error will be raised
when running a command that requires an environment.
"""
