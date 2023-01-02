import dataclasses
import pathlib

from twcollect.config import parse_credentials_file

from twcompose.backends import get_collections_backend
from twcompose.compose import TwitterComposeModel
from twcompose.rules import TwitterRuleAPI
from twcompose.utils import print_object_as_yaml


def status_command(
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials_file: pathlib.Path,
):
    """Print the current status of the defined streams"""
    backend = get_collections_backend()

    # Getting installed rules
    credentials = parse_credentials_file(credentials_file)
    rules = TwitterRuleAPI(twitter_token=credentials.__root__["twitter_token"])
    active_rules = rules.get()

    # Getting status of collection
    is_collection_running = backend.is_running(project_name)

    # Printing results
    print_object_as_yaml(
        {"Active rules": [dataclasses.asdict(r) for r in active_rules]}
    )
    if is_collection_running:
        print(f"Tweets collection is running for {project_name}.")
    else:
        print(f"Tweets collection is stopped for {project_name}.")
