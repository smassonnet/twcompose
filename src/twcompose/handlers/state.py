import argparse
import dataclasses
import pathlib
from typing import Any, Dict, List, Optional

import tweepy

from twcompose.compose import TwitterComposeModel


@dataclasses.dataclass
class CommandHandlerState:
    """Common state used by command handlers

    Attributes:
        project_name (str): The name of the twitter-compose project
        twitter_compose_file (pathlib.Path): The path to the twitter
            compose file
        credentials_file (pathlib.Path): The path to the credentials
            file.
        command_args (dict[str, Any]): Additional command line arguments
        twitter_client (tweepy.Client | None, optional): The tweepy client
    """

    # Base config
    project_name: str
    twitter_compose_file: pathlib.Path
    credentials_file: pathlib.Path
    log_level: str
    command_args: Dict[str, Any]

    # Config parsing
    twitter_compose_config: Optional[TwitterComposeModel] = None
    # Twitter client command handler
    twitter_client: Optional[tweepy.Client] = None
    # Tweet volume estimation
    volume_per_rule: Optional[Dict[str, int]] = None
    # Stdout messages
    messages: List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def from_argparse(cls, arguments: argparse.Namespace):
        command_arguments = arguments.__dict__.copy()
        del command_arguments["tc_file"]
        del command_arguments["credentials"]
        del command_arguments["project_name"]
        del command_arguments["func"]
        del command_arguments["command"]
        del command_arguments["log_level"]
        return cls(
            project_name=arguments.project_name,
            twitter_compose_file=arguments.tc_file,
            credentials_file=arguments.credentials,
            log_level=arguments.log_level,
            command_args=command_arguments,
        )
