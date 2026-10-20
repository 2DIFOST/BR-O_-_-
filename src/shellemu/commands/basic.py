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


def cmd_echo(shell, args: list[str]) -> Response:
    """Print the arguments separated by single spaces."""
    response = Response()
    response.out(" ".join(args))
    return response
