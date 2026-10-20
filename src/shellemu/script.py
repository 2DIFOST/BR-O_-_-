"""Reading of startup scripts."""
from .errors import ScriptError


def read_script(path: str) -> list[str]:
    """Return the lines of a startup script (UTF-8 text file)."""
    try:
        with open(path, encoding="utf-8") as file:
            return file.read().splitlines()
    except OSError as error:
        raise ScriptError(
            f"cannot read script '{path}': {error.strerror}"
        ) from error
    except UnicodeDecodeError as error:
        raise ScriptError(
            f"cannot read script '{path}': not a UTF-8 text file"
        ) from error
