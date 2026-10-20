"""Information about the real OS the emulator is running on."""
import getpass
import os
import socket

DEFAULT_USER = "user"
DEFAULT_HOST = "localhost"
TITLE_PREFIX = "Эмулятор"


def get_username() -> str:
    """Return the name of the current OS user."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return os.environ.get("USER", DEFAULT_USER)


def get_hostname() -> str:
    """Return the host name of the current machine."""
    return socket.gethostname() or DEFAULT_HOST


def get_identity() -> str:
    """Return the ``username@hostname`` string."""
    return f"{get_username()}@{get_hostname()}"


def make_title() -> str:
    """Return the window title, e.g. ``Эмулятор - [user@host]``."""
    return f"{TITLE_PREFIX} - [{get_identity()}]"
