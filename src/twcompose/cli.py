import argparse
import pathlib
from typing import Any, Callable, Optional

from twcollect.utils import (
    add_credentials_file_argument,
    add_log_level_argument,
    setup_logging,
    valid_file_type,
)

from twcompose.commands.config import config_command
from twcompose.commands.status import status_command
from twcompose.commands.stop import stop_command
from twcompose.commands.update import update_command
from twcompose.commands.volume import volume_command
from twcompose.compose import parse_compose_file


def add_subparser(
    subparsers: "argparse._SubParsersAction[argparse.ArgumentParser]",
    name: str,
    command_fun: Callable[..., Any],
    help: Optional[str] = None,
) -> argparse.ArgumentParser:
    """Add a subparser for a subcommand

    Args:
        subparsers (_SubParsersAction):
        name (str): The name of the parser command
        command_fun (Callable): The function to execute the command
        help (str | None): The help text for the command
    """
    command = subparsers.add_parser(name, help=help)
    command.set_defaults(func=command_fun)
    return command


def cli() -> None:
    parser = argparse.ArgumentParser(
        "twitter-compose", description="Manage Twitter streams"
    )

    # General arguments
    parser.add_argument(
        "-f",
        "--file",
        dest="tc_file",
        type=valid_file_type,
        default="twitter-compose.yml",
        help="The file name of the twitter-compose configuration",
    )
    parser.add_argument(
        "-p",
        "--project-name",
        dest="project_name",
        default=pathlib.Path().absolute().name,
        help="Name of the current project",
    )
    add_credentials_file_argument(parser)
    add_log_level_argument(parser)

    # Commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Config
    add_subparser(
        subparsers, "config", config_command, help="Show parsed configuration"
    )

    # Update
    update_parser = add_subparser(
        subparsers, "up", update_command, help="Update Twitter streams"
    )
    update_parser.add_argument(
        "--check",
        action="store_true",
        help="Do not perform changes, prints to console only",
    )

    # Status
    add_subparser(
        subparsers, "status", status_command, help="Status of defined streams"
    )

    # Stop
    add_subparser(subparsers, "stop", stop_command, help="Stop Twitter streams")

    # Volume estimation
    volume_parser = add_subparser(
        subparsers,
        "volume",
        volume_command,
        help="Estimation of the monthly volume of streams",
    )
    volume_parser.add_argument(
        "--min",
        default=None,
        type=int,
        help="Returns only rule with a volume larger that this minimum",
    )
    volume_parser.add_argument(
        "volume_rules",
        nargs="*",
        default=None,
        help="Test the given rules instead of the ones from the twitter-compose file",
    )

    # Remove
    # add_subparser(subparsers, "rm", rm_command, help="Remove Twitter streams")

    # Getting arguments
    arguments: argparse.Namespace = parser.parse_args()
    setup_logging(arguments.log_level)

    # Getting compose file
    compose = parse_compose_file(arguments.tc_file)

    # Calling the command function
    command_arguments = arguments.__dict__.copy()
    del command_arguments["tc_file"]
    del command_arguments["credentials"]
    del command_arguments["project_name"]
    del command_arguments["func"]
    del command_arguments["command"]
    del command_arguments["log_level"]
    arguments.func(
        arguments.project_name, compose, arguments.credentials, **command_arguments
    )
