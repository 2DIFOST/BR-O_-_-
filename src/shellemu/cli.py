"""Command-line entry point of the emulator."""
import sys

from .config import Config, parse_args
from .console import ConsoleOutput, run_console
from .errors import GuiUnavailableError
from .session import Session
from .shell import Shell
from .sysinfo import get_identity, make_title

EXIT_OK = 0
EXIT_ERROR = 1


def start_console(shell: Shell, config: Config) -> Session:
    """Run the emulator in the terminal."""
    session = Session(shell, ConsoleOutput())
    session.startup(config)
    run_console(session)
    return session


def start_gui(shell: Shell, config: Config) -> Session | None:
    """Run the emulator in a window; None if no window can be opened."""
    try:
        from .gui import EmulatorWindow
        window = EmulatorWindow(shell, make_title())
    except (ImportError, GuiUnavailableError) as error:
        print(f"shellemu: GUI is unavailable ({error}); "
              "try --no-gui", file=sys.stderr)
        return None
    window.run(config)
    return window.session


def main(argv: list[str] | None = None) -> int:
    """Parse parameters, start the emulator and return the exit code."""
    config = parse_args(argv)
    shell = Shell(get_identity())
    if config.no_gui:
        session = start_console(shell, config)
    else:
        session = start_gui(shell, config)
    if session is None or not session.startup_ok:
        return EXIT_ERROR
    return EXIT_OK
