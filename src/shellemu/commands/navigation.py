"""Commands for navigating the file system: ``ls`` and ``cd``.

At this stage both commands are stubs: they print their own name
and the arguments they were called with.
"""
from ..response import Response


def format_call(name: str, args: list[str]) -> str:
    """Return the command name followed by its arguments."""
    return " ".join([name, *args])


def cmd_ls(shell, args: list[str]) -> Response:
    """Stub of ``ls``: print the name and the arguments."""
    response = Response()
    response.out(format_call("ls", args))
    return response


def cmd_cd(shell, args: list[str]) -> Response:
    """Stub of ``cd``: print the name and the argument."""
    response = Response()
    match args:
        case [] | [_]:
            response.out(format_call("cd", args))
        case _:
            response.err("cd: too many arguments")
    return response
