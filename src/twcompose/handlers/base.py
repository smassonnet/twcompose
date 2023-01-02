import dataclasses
from typing import Optional

from typing_extensions import Self

from twcompose.handlers.state import CommandHandlerState


@dataclasses.dataclass
class CommandHandler:
    def __post_init__(self):
        self.next_handler: Optional["CommandHandler"] = None

    def handle(self, state: CommandHandlerState):
        """Handle the current command state

        By default passes to the next handler
        """
        if self.next_handler is not None:
            self.next_handler.handle(state)

    def set_next_handler(self, handler: "CommandHandler") -> Self:
        self.next_handler = handler
        return self

    def chain(self, *handlers: "CommandHandler") -> Self:
        """Append the handlers as a chain"""
        current: CommandHandler = self
        for h in handlers:
            current.set_next_handler(h)
            current = h
        return self
