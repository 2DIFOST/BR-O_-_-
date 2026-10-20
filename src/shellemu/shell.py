"""Core of the emulator: executes commands, independent of the GUI."""
from .commands import COMMANDS
from .parser import parse_line
from .response import STATUS_NOT_FOUND, Response


class Shell:
    """State of the shell and the logic of command execution."""

    def __init__(self, identity: str = "user@host") -> None:
        """Create a shell; ``identity`` is shown in the prompt."""
        self.identity = identity

    def prompt(self) -> str:
        """Return the input prompt."""
        return f"{self.identity}:~$ "

    def execute(self, line: str) -> Response:
        """Parse and execute one input line."""
        words = parse_line(line)
        if not words:
            return Response()
        name, *args = words
        handler = COMMANDS.get(name)
        if handler is None:
            response = Response()
            response.err(f"{name}: command not found", STATUS_NOT_FOUND)
            return response
        return handler(self, args)
