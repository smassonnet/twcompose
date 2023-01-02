import pathlib
from typing import Iterable, Set, Union

import yaml

from twcompose.backends.abstract import AbstractCollectionBackend
from twcompose.compose import TwitterComposeModel
from twcompose.rules import TwitterRule


def print_object_as_yaml(o: Union[dict, Iterable], **kwargs) -> None:
    print(yaml.safe_dump(o), **kwargs)


def ensure_backend_stopped(backend: AbstractCollectionBackend, project_name: str):
    if backend.is_running(project_name):
        print(f"Stopping stream collector {project_name}...")
        backend.stop(project_name)
        print(f"Stopping stream collector {project_name}... Done.")
    else:
        print(f"Already stopped stream collector {project_name}.")


def update_backend(
    backend: AbstractCollectionBackend,
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials_file: pathlib.Path,
):
    print(f"Starting stream collector {project_name}...")
    backend.update(project_name, compose_config, credentials_file)
    print(f"Starting stream collector {project_name}... Done.")


def get_rules_from_compose_config(
    compose_config: TwitterComposeModel,
) -> Set[TwitterRule]:
    return {
        TwitterRule.from_rule_model(r)
        for rules in compose_config.streams.values()
        for r in rules
    }
