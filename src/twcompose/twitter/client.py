from functools import lru_cache

import tweepy


@lru_cache(1)  # Only one client per twitter-compose command
def twitter_client_factory(twitter_token: str) -> tweepy.Client:
    return tweepy.Client(twitter_token, wait_on_rate_limit=True)
