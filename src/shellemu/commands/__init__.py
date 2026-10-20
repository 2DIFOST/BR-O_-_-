"""Registry of the commands supported by the emulator."""
from collections.abc import Callable

from ..response import Response
from .basic import cmd_echo, cmd_exit
from .files import cmd_cp, cmd_rm
from .navigation import cmd_cd, cmd_ls
from .service import cmd_vfs_info, cmd_vfs_tree
from .text import cmd_wc

Handler = Callable[[object, list[str]], Response]

COMMANDS: dict[str, Handler] = {
    "cd": cmd_cd,
    "cp": cmd_cp,
    "echo": cmd_echo,
    "exit": cmd_exit,
    "ls": cmd_ls,
    "rm": cmd_rm,
    "vfs-info": cmd_vfs_info,
    "vfs-tree": cmd_vfs_tree,
    "wc": cmd_wc,
}
