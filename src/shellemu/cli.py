"""Command-line entry point of the emulator."""
from .gui import EmulatorWindow
from .shell import Shell
from .sysinfo import get_identity, make_title


def main() -> int:
    """Start the emulator in a graphical window."""
    window = EmulatorWindow(Shell(get_identity()), make_title())
    window.run()
    return 0
