import pathlib
from typing import Dict, cast

from twcompose.compose import TwitterComposeModel
from twcompose.handlers.messages import PrintMessagesHandler, SaveMessageHandler
from twcompose.handlers.state import CommandHandlerState
from twcompose.handlers.twitter import SetTwitterClientHandler
from twcompose.handlers.volume import VolumeEstimatorCommandHandler


def volume_command(
    project_name: str,
    compose_config: TwitterComposeModel,
    credentials_file: pathlib.Path,
    **kwargs,
):
    # Creating a state
    state = CommandHandlerState(
        project_name=project_name,
        twitter_compose_file=pathlib.Path(),
        credentials_file=credentials_file,
        log_level="",
        command_args=kwargs,
        twitter_compose_config=compose_config,
    )

    # Define and run handlers chain
    handler = SetTwitterClientHandler().chain(
        # Estimate the volume of rules
        VolumeEstimatorCommandHandler(),
        # Saves the volume as message
        SaveMessageHandler(
            state_to_message=lambda s: "\n".join(
                f"{r}: {v}" for r, v in cast(Dict[str, int], s.volume_per_rule).items()
            )
        ),
        # Print the messages
        PrintMessagesHandler(),
    )
    handler.handle(state)
