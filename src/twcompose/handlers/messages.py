import dataclasses
from typing import Callable, Optional

from twcompose.handlers.base import CommandHandler
from twcompose.handlers.state import CommandHandlerState


@dataclasses.dataclass
class PrintMessagesHandler(CommandHandler):
    """Print message from `state.messages`

    Attributes:
        default_message (str, optional): Used if `state.messages` is empty.
            Defaults to `None`.
        print_func (Callable[[str], None], optional): The print function to use.
            Defaults to built-in `print`.
    """

    default_message: Optional[str] = None
    print_func: Callable[[str], None] = print

    def handle(self, state: CommandHandlerState):
        if state.messages:
            for m in state.messages:
                self.print_func(m)
        elif self.default_message:
            self.print_func(self.default_message)

        super().handle(state)


@dataclasses.dataclass
class SaveMessageHandler(CommandHandler):
    """Adds a new message from the state"""

    state_to_message: Callable[[CommandHandlerState], str]

    def handle(self, state: CommandHandlerState):
        state.messages.append(self.state_to_message(state))
        super().handle(state)
