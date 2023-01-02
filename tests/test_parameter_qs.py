import pytest

from twcompose.compose import TwitterStreamParametersModel


@pytest.mark.parametrize(
    ("parameters_model", "expected_qs"),
    [
        (TwitterStreamParametersModel(), ""),
        (
            TwitterStreamParametersModel(expansions=["attachments.poll_ids"]),
            "expansions=attachments.poll_ids",
        ),
        (
            TwitterStreamParametersModel(
                expansions=["attachments.poll_ids"], tweet_fields=["text", "source"]
            ),
            "expansions=attachments.poll_ids&tweet.fields=text%2Csource",
        ),
    ],
    ids=["empty", "one", "list"],
)
def test_parameter_querystring(
    parameters_model: TwitterStreamParametersModel, expected_qs: str
):
    assert parameters_model.to_querystring() == expected_qs
