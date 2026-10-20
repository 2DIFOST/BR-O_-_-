"""General-purpose shell commands."""
from ..response import Response


def cmd_exit(shell, args: list[str]) -> Response:
    """Finish the work of the emulator."""
    response = Response()
    match args:
        case []:
            response.should_exit = True
        case _:
            response.err("exit: too many arguments")
    return response
