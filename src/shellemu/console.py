"""Terminal mode of the emulator (``--no-gui``).

It uses the same shell core and is convenient for automated tests
and for machines without a display.
"""
import sys

from .session import KIND_ERROR, Session


class ConsoleOutput:
    """Output writing to stdout; errors go to stderr."""

    def write(self, text: str, kind: str) -> None:
        """Print a line and flush so the streams stay ordered."""
        stream = sys.stderr if kind == KIND_ERROR else sys.stdout
        print(text, file=stream, flush=True)


def read_line(prompt: str, interactive: bool) -> str | None:
    """Read a line from stdin; return None at the end of input."""
    if interactive:
        try:
            return input(prompt)
        except EOFError:
            print()
            return None
    line = sys.stdin.readline()
    if not line:
        return None
    return line.rstrip("\n")


def run_console(session: Session) -> None:
    """Read and execute lines until ``exit`` or end of input.

    When stdin is not a terminal the typed lines are echoed, so the
    output looks like a dialog.
    """
    interactive = sys.stdin.isatty()
    while not session.finished:
        line = read_line(session.shell.prompt(), interactive)
        if line is None:
            return
        if interactive:
            session.execute_line(line)
        else:
            session.run_line(line)
