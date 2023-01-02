from twcollect.config import parse_credentials_file

from twcompose.handlers.base import CommandHandler
from twcompose.handlers.state import CommandHandlerState
from twcompose.twitter.client import twitter_client_factory


class SetTwitterClientHandler(CommandHandler):
    """Defines the twitter client

    Sets the `twitter_client` attribute of state
    """

    def handle(self, state: CommandHandlerState):
        credentials = parse_credentials_file(state.credentials_file)
        twitter_token = credentials.__root__["twitter_token"]
        state.twitter_client = twitter_client_factory(twitter_token)
        super().handle(state)
