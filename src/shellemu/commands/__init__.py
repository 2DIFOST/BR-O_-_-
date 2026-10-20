"""Registry of the commands supported by the emulator."""
from collections.abc import Callable

from ..response import Response
from .basic import cmd_exit
from .navigation import cmd_cd, cmd_ls
from .service import cmd_vfs_info, cmd_vfs_tree

Handler = Callable[[object, list[str]], Response]

COMMANDS: dict[str, Handler] = {
    "cd": cmd_cd,
    "exit": cmd_exit,
    "ls": cmd_ls,
    "vfs-info": cmd_vfs_info,
    "vfs-tree": cmd_vfs_tree,
}
