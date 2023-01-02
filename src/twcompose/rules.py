import dataclasses
import functools
import logging
import time
from typing import Any, Dict, List, Optional, Set

import requests
from typing_extensions import Final, TypeAlias

from twcompose.compose import TwitterStreamRuleModel

_logger = logging.getLogger(__name__)


_Error: TypeAlias = "dict[str, Any]"


@dataclasses.dataclass(frozen=True)
class TwitterRule:
    value: str
    tag: Optional[str] = None
    id: Optional[str] = None

    @classmethod
    def from_rule_model(cls, compose_rule: TwitterStreamRuleModel) -> "TwitterRule":
        return cls(tag=compose_rule.tag, value=compose_rule.value)

    def is_equivalent(self, other: "TwitterRule") -> bool:
        """True is two rule have the same definition.

        This means same value and tag
        """
        return self.value == other.value and self.tag == other.tag


@dataclasses.dataclass
class TwitterRulesDiff:
    """Class that represents changes to be posted to Twitter's rule endpoint"""

    add: List[TwitterRule] = dataclasses.field(default_factory=list)
    delete: List[TwitterRule] = dataclasses.field(default_factory=list)

    def is_empty(self) -> bool:
        """True if the object does not contain changes that need to be pushed"""
        return len(self.add) == 0 and len(self.delete) == 0

    def to_twitter_payload(self) -> List[dict]:
        """Transforms the diff into a payload that can be posted on Twitter"""
        ret: List[dict] = []
        if self.delete:
            ret.append({"delete": {"ids": [r.id for r in self.delete]}})
        if self.add:
            ret.append({"add": [dataclasses.asdict(r) for r in self.add]})
        return dict_remove_none_fields(ret)


@functools.singledispatch
def dict_remove_none_fields(d):
    return d


@dict_remove_none_fields.register
def _dict_dispatch(d: dict) -> dict:
    ret = {}
    for key, value in d.items():
        # If the value is None we skip
        if value is None:
            continue

        # Otherwise we add it to the returned dict
        ret[key] = dict_remove_none_fields(value)
    return ret


@dict_remove_none_fields.register
def _list_dispatch(d: list) -> list:
    return [dict_remove_none_fields(element) for element in d]


def compute_rule_changes(
    current_rules: Set[TwitterRule], new_rules: Set[TwitterRule]
) -> TwitterRulesDiff:
    """Computes the updates to perform to get to the new rules from the current rules

    Args:
        current_rules (list[TwitterRule]): The rules currently saved on Twitter
        new_rules (list[TwitterRule]): The desired rules after the update

    Returns:
        TwitterPostRules: The changes to send to the Twitter's rule endpoint.
    """
    # Making a copy of rules set
    new_rules = new_rules.copy()

    to_delete: Set[TwitterRule] = set()
    for current in current_rules:
        matching_new_rule = next(
            (r for r in new_rules if current.is_equivalent(r)), None
        )

        if matching_new_rule is None:
            # No match, the rule has to be deleted
            if current.id is None:
                raise ValueError(
                    "Cannot handle TwitterRule with id=None when planning its deletion"
                )
            to_delete.add(current)
        else:
            # The rule is in the new rules, we do not delete it
            # And we remove it from the new rules to not add it again
            new_rules.discard(matching_new_rule)
    return TwitterRulesDiff(add=list(new_rules), delete=list(to_delete))


@dataclasses.dataclass
class TwitterRuleAPI:
    twitter_token: str
    url_rules: Final[str] = dataclasses.field(
        init=False, default="https://api.twitter.com/2/tweets/search/stream/rules"
    )

    def _twitter_request(self, method: str, url: str, **kwargs) -> requests.Response:
        kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault("Authorization", f"Bearer {self.twitter_token}")
        while True:
            response: requests.Response = getattr(requests, method)(url, **kwargs)

            # If we hit a rate limit, we wait and continue to the next loop
            if response.status_code == 429:
                time_to_sleep: float = (
                    int(response.headers["x-rate-limit-reset"]) - time.time()
                )
                _logger.info(
                    "Too many requests to Twitter, waiting for rate limit: "
                    f"{time_to_sleep} seconds"
                )
                time.sleep(time_to_sleep)
                continue

            # Otherwise proceed normally and raise for abnormal status
            if not response.ok:
                _logger.info(
                    f"Received error from Twitter with payload: {response.text}"
                )
                response.raise_for_status()
            return response

    def get(self) -> Set[TwitterRule]:
        """Gets twitter rules"""
        response = self._twitter_request("get", self.url_rules)
        # Getting rules
        payload: Dict[str, Any] = response.json()
        return {TwitterRule(**r) for r in payload.get("data", [])}

    def post(self, changes: TwitterRulesDiff, dry_run: bool = False) -> List[_Error]:
        """Update twitter rules from the given changes"""
        errors: List[_Error] = []
        for payload in changes.to_twitter_payload():
            response = self._twitter_request(
                "post", self.url_rules, params={"dry_run": dry_run}, json=payload
            )
            errors += response.json().get("errors", [])

        return errors
