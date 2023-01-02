"""Interface to get the monthly estimated number of tweets for a query"""
import dataclasses
from typing import ClassVar, cast

import tweepy


@dataclasses.dataclass
class MonthlyTwitterCountEstimator:
    """Estimate the monthly number of tweets for a rule

    Attributes:
        tweepy_client (tweepy.Client): The tweepy Client
            used to call the Twitter API.
    """

    tweepy_client: tweepy.Client

    url_tweets_counts: ClassVar[str] = "https://api.twitter.com/2/tweets/counts/recent"

    def estimate(self, rule: str) -> int:
        """Estimates the monthly number of tweets matching the given rule

        Args:
            rule (str): Twitter rule query

        Returns:
            int: Estimated monthly number of tweets
        """
        # Calling the twitter API
        response = cast(
            tweepy.Response,
            self.tweepy_client.get_recent_tweets_count(rule, granularity="day"),
        )

        # No matching tweets
        if response.data is None:
            return 0

        # Returning the estimated number of tweet for 31 days
        return int(
            sum(r["tweet_count"] for r in response.data) / len(response.data) * 31
        )
