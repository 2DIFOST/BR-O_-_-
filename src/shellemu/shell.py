"""Core of the emulator: executes commands, independent of the GUI."""
from .commands import COMMANDS
from .parser import parse_line
from .response import STATUS_NOT_FOUND, Response
from .vfs import Vfs


class Shell:
    """State of the shell and the logic of command execution."""

    def __init__(
        self, identity: str = "user@host", vfs: Vfs | None = None
    ) -> None:
        """Create a shell; ``identity`` is shown in the prompt."""
        self.identity = identity
        self.vfs = vfs if vfs is not None else Vfs()
        self.cwd = self.vfs.root

    def attach_vfs(self, vfs: Vfs) -> None:
        """Replace the VFS; the current directory becomes its root."""
        self.vfs = vfs
        self.cwd = vfs.root

    def prompt(self) -> str:
        """Return the input prompt with the current directory."""
        return f"{self.identity}:{self.cwd.path}$ "

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
