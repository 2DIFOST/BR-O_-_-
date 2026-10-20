"""Registry of the commands supported by the emulator."""
from collections.abc import Callable

from ..response import Response
from .basic import cmd_exit
from .navigation import cmd_cd, cmd_ls

Handler = Callable[[object, list[str]], Response]

COMMANDS: dict[str, Handler] = {
    "cd": cmd_cd,
    "exit": cmd_exit,
    "ls": cmd_ls,
}
