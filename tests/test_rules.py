from typing import Set

import pytest

from twcompose.rules import TwitterRule, TwitterRulesDiff, compute_rule_changes

COP26_RULE = TwitterRule(value="#cop26", tag="COP26")
COP26_NEW_TAG = TwitterRule(value="#cop26", tag="COP26 hashtag")
COP26_RULE_ID = "12345"
COP26_RULE_WITH_ID = TwitterRule(value="#cop26", tag="COP26", id=COP26_RULE_ID)


@pytest.mark.parametrize(
    ("current_rules", "new_rules", "post_payload"),
    [
        (set(), {COP26_RULE}, TwitterRulesDiff(add=[COP26_RULE])),
        ({COP26_RULE_WITH_ID}, set(), TwitterRulesDiff(delete=[COP26_RULE_WITH_ID])),
        (
            {COP26_RULE_WITH_ID},
            {COP26_NEW_TAG},
            TwitterRulesDiff(delete=[COP26_RULE_WITH_ID], add=[COP26_NEW_TAG]),
        ),
        (
            {COP26_RULE_WITH_ID},
            {COP26_RULE},
            TwitterRulesDiff(),
        ),
    ],
    ids=["current_empty", "new_empty", "rename_tag", "no_changes"],
)
def test_compute_rule_changes(
    current_rules: Set[TwitterRule],
    new_rules: Set[TwitterRule],
    post_payload: TwitterRulesDiff,
):
    # Checking the function returns as expected
    assert compute_rule_changes(current_rules, new_rules) == post_payload


@pytest.mark.parametrize(
    ("rules_diff", "payload"),
    [
        (
            TwitterRulesDiff(delete=[COP26_RULE_WITH_ID]),
            [{"delete": {"ids": [COP26_RULE_ID]}}],
        ),
        (
            TwitterRulesDiff(add=[COP26_RULE]),
            [{"add": [{"value": COP26_RULE.value, "tag": COP26_RULE.tag}]}],
        ),
        (
            TwitterRulesDiff(add=[COP26_RULE], delete=[COP26_RULE_WITH_ID]),
            [
                {"delete": {"ids": [COP26_RULE_ID]}},
                {"add": [{"value": COP26_RULE.value, "tag": COP26_RULE.tag}]},
            ],
        ),
    ],
    ids=["delete", "add", "all"],
)
def test_rules_diff_to_payload(rules_diff: TwitterRulesDiff, payload: dict):
    assert rules_diff.to_twitter_payload() == payload
