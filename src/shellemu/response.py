"""Result of executing one shell command."""
from dataclasses import dataclass, field

STATUS_OK = 0
STATUS_ERROR = 1
STATUS_NOT_FOUND = 127


@dataclass
class Message:
    """One line of output: regular text or an error message."""

    text: str
    is_error: bool = False


@dataclass
class Response:
    """Messages printed by a command together with its exit status."""

    messages: list[Message] = field(default_factory=list)
    status: int = STATUS_OK
    should_exit: bool = False

    def out(self, text: str) -> None:
        """Add a regular output line."""
        self.messages.append(Message(text))

    def err(self, text: str, status: int = STATUS_ERROR) -> None:
        """Add an error line and mark the command as failed."""
        self.messages.append(Message(text, is_error=True))
        self.status = status

    @property
    def ok(self) -> bool:
        """Return True if the command finished successfully."""
        return self.status == STATUS_OK
