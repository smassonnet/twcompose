"""Parse the twitter-compose.yml file"""
import pathlib
import warnings
from typing import Any, Dict, Iterable, List, Set, Tuple, Type, TypeVar, Union, cast
from urllib.parse import urlencode

import yaml
from pydantic import BaseModel, Field, StrictInt, StrictStr, root_validator
from typing_extensions import Literal

_T = TypeVar("_T", bound=BaseModel)


class TwitterOutputDriver(BaseModel):
    driver: str
    path: str
    options: Dict[str, Union[StrictStr, StrictInt]]


class TwitterStreamRuleModel(BaseModel):
    value: str
    # Tags are not required on Twitter but we force it
    # in order to match the rules of returned tweets
    tag: str


TwitterParameterExpansions = Literal[
    "attachments.poll_ids",
    "attachments.media_keys",
    "author_id",
    "entities.mentions.username",
    "geo.place_id",
    "in_reply_to_user_id",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
]
TwitterParameterMediaFields = Literal[
    "duration_ms",
    "height",
    "media_key",
    "preview_image_url",
    "type",
    "url",
    "width",
    "public_metrics",
    "alt_text",
]
TwitterParameterPlaceFields = Literal[
    "contained_within",
    "country",
    "country_code",
    "full_name",
    "geo",
    "id",
    "name",
    "place_type",
]
TwitterParameterPollFields = Literal[
    "duration_minutes", "end_datetime", "id", "options", "voting_status"
]
TwitterParameterTweetFields = Literal[
    "attachments",
    "author_id",
    "context_annotations",
    "conversation_id",
    "created_at",
    "entities",
    "geo",
    "id",
    "in_reply_to_user_id",
    "lang",
    "public_metrics",
    "possibly_sensitive",
    "referenced_tweets",
    "reply_settings",
    "source",
    "text",
    "withheld",
]
TwitterParameterUserFields = Literal[
    "created_at",
    "description",
    "entities",
    "id",
    "location",
    "name",
    "pinned_tweet_id",
    "profile_image_url",
    "protected",
    "public_metrics",
    "url",
    "username",
    "verified",
    "withheld",
]


class TwitterStreamParametersModel(BaseModel):
    expansions: List[TwitterParameterExpansions] = Field(default_factory=list)
    media_fields: List[TwitterParameterMediaFields] = Field(default_factory=list)
    place_fields: List[TwitterParameterPlaceFields] = Field(default_factory=list)
    poll_fields: List[TwitterParameterPollFields] = Field(default_factory=list)
    tweet_fields: List[TwitterParameterTweetFields] = Field(default_factory=list)
    user_fields: List[TwitterParameterUserFields] = Field(default_factory=list)

    def to_querystring(self) -> str:
        qs_dict: Dict[str, str] = {}
        for field, value in self.dict().items():
            # We skip if the value is empty
            if not value:
                continue
            # Replace _fields with .fields
            if field.endswith("_fields"):
                field = f"{field[:-7]}.fields"
            # Adding the value to querystring joining lists with commas
            qs_dict[field] = ",".join(value)

        return urlencode(qs_dict)


class TwitterComposeModel(BaseModel):
    """twitter-compose file model"""

    image_tag: StrictStr
    output: TwitterOutputDriver
    parameters: TwitterStreamParametersModel
    streams: Dict[str, List[TwitterStreamRuleModel]]
    image_name: str = "ghcr.io/smassonnet/twcollect"

    @root_validator
    def check_tag_unique_to_a_stream(cls, values: Dict[str, Any]):
        # Structure to hold the set of groups that mentions a tag
        # Warnings will be raised if tags are found in multiple groups
        tags_to_stream_names: Dict[str, Set[str]] = {}
        streams_definitions = cast(
            Iterable[Tuple[str, List[TwitterStreamRuleModel]]],
            values["streams"].items(),
        )
        for stream_group, rules in streams_definitions:
            for r in rules:
                tags_to_stream_names.setdefault(r.tag, set())

                # If there are already 2 matching groups,
                # we skip as we already printed a warning
                if len(tags_to_stream_names[r.tag]) == 2:
                    continue

                tags_to_stream_names[r.tag].add(stream_group)
                if len(tags_to_stream_names[r.tag]) == 2:
                    # More that 2 stream groups, warning
                    stream_groups_str = ",".join(tags_to_stream_names[r.tag])
                    warnings.warn(
                        f"Found tag '{r.tag}' in two stream "
                        f"groups {stream_groups_str}, "
                        "this can lead to inconsistent behaviour "
                        "when retrieving tweets for a stream group"
                    )

        return values


def parse_file_from_pydantic_model(path: pathlib.Path, model: Type[_T]) -> _T:
    with path.open() as cf:
        return model.parse_obj(yaml.safe_load(cf))


def parse_compose_file(twitter_compose_path: pathlib.Path) -> TwitterComposeModel:
    return parse_file_from_pydantic_model(twitter_compose_path, TwitterComposeModel)
