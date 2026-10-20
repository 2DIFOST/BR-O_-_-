"""Command-line parameters of the emulator."""
import argparse
from dataclasses import dataclass

NOT_SET = "(not set)"


@dataclass(frozen=True)
class Config:
    """Parameters given by the user at start."""

    vfs_path: str | None = None
    script_path: str | None = None
    no_gui: bool = False


def build_parser() -> argparse.ArgumentParser:
    """Create the parser of command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="shellemu",
        description="Emulator of a UNIX-like shell with a virtual "
                    "file system.",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="path to the physical location of the VFS (XML file)",
    )
    parser.add_argument(
        "--script", metavar="PATH",
        help="path to the startup script with emulator commands",
    )
    parser.add_argument(
        "--no-gui", action="store_true",
        help="work in the terminal instead of a window (for tests/CI)",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> Config:
    """Parse arguments (``sys.argv`` by default) into a Config."""
    namespace = build_parser().parse_args(argv)
    return Config(namespace.vfs, namespace.script, namespace.no_gui)


def show_value(value: object) -> str:
    """Return a printable form of a parameter value."""
    return NOT_SET if value is None else str(value)


def debug_lines(config: Config) -> list[str]:
    """Return the debug output listing all parameters."""
    return [
        "[debug] parameters:",
        f"[debug]   vfs    = {show_value(config.vfs_path)}",
        f"[debug]   script = {show_value(config.script_path)}",
        f"[debug]   no-gui = {config.no_gui}",
    ]
