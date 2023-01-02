import dataclasses
import pathlib
from typing import Optional

from twcollect.config import parse_credentials_file

from twcompose.backends import get_collections_backend
from twcompose.backends.abstract import AbstractCollectionBackend, CollectorDoesNotExist
from twcompose.compose import TwitterComposeModel
from twcompose.rules import (
    TwitterRuleAPI,
    TwitterRulesDiff,
    compute_rule_changes,
    dict_remove_none_fields,
)
from twcompose.utils import (
    get_rules_from_compose_config,
    print_object_as_yaml,
    update_backend,
)


def _verify_rule_changes(
    twitter_api: TwitterRuleAPI, compose_config: TwitterComposeModel
) -> Optional[TwitterRulesDiff]:
    # Getting twitter and compose rules
    twitter_rules = twitter_api.get()
    compose_rules = get_rules_from_compose_config(compose_config)
    # Computing the changes between twitter and compose rules
    changes = compute_rule_changes(twitter_rules, compose_rules)

    # If changes is empty returns None
    if changes.is_empty():
        return None

    # Stream rules update
    rules_update = dict_remove_none_fields(dataclasses.asdict(changes))
    print_object_as_yaml(
        {"> Stream rules will be updated as follows": rules_update},
        end="",
    )
    return changes


def _verify_collector_changes(
    backend: AbstractCollectionBackend,
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials_file: pathlib.Path,
) -> bool:
    try:
        differences = backend.diff(project_name, compose_config, credentials_file)
    except CollectorDoesNotExist:
        print_object_as_yaml(["Stream collector should be created"])
        # There are changes
        return True

    # Collecting changes on collector status and options
    diff_object: list = []
    if not backend.is_running(project_name):
        diff_object.append("Stream collection needs to be started")
    if len(differences) > 0:
        diff_object.append(
            {
                "Collector will be updated as follows": {
                    k: dataclasses.asdict(v) for k, v in differences.items()
                }
            }
        )

    if len(diff_object) == 0:
        return False

    print_object_as_yaml(diff_object)
    return True


def update_command(
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials_file: pathlib.Path,
    check: bool = False,
):
    # Getting the connection to backend
    backend = get_collections_backend()

    # Getting token and connection to Twitter
    credentials = parse_credentials_file(credentials_file)
    twitter_token = credentials.__root__["twitter_token"]
    twitter_api = TwitterRuleAPI(twitter_token)

    # Printing and getting changes
    rules_changes = _verify_rule_changes(twitter_api, compose_config)

    # Getting container and changes
    collector_changed = _verify_collector_changes(
        backend,
        project_name,
        compose_config,
        credentials_file,
    )

    if rules_changes is None and not collector_changed:
        # If there is nothing to do
        print("Nothing to do.")
        return

    if check:
        if rules_changes is not None:
            # Make sure rules are valid
            errors = twitter_api.post(rules_changes, dry_run=True)
            if errors:
                raise ValueError(f"Couldn't create all rules: {errors}")

        # Do not perform changes and return
        return

    if rules_changes is not None:
        # We need to push the changes to Twitter
        print("Updating Twitter rules...")
        errors = twitter_api.post(rules_changes)
        if errors:
            raise ValueError(f"Couldn't create all rules: {errors}")
        print("Updating Twitter rules... Done.")

    if collector_changed:
        # Make sure the collection is started
        update_backend(backend, project_name, compose_config, credentials_file)
