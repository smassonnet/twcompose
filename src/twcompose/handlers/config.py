from twcompose.compose import parse_compose_file
from twcompose.handlers import CommandHandler
from twcompose.handlers.state import CommandHandlerState


class ComposeConfigParserHandler(CommandHandler):
    def handle(self, state: CommandHandlerState):
        # Parsing the compose file
        state.twitter_compose_config = parse_compose_file(state.twitter_compose_file)

        # Passing to the next handler
        super().handle(state)
