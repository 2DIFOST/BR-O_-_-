"""Parsing of the short options of commands (``-l``, ``-la``)."""
from ..errors import UsageError

OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"


def is_option(arg: str) -> bool:
    """Return True for arguments like ``-l`` or ``--long``."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def split_options(
    command: str, args: list[str], allowed: str
) -> tuple[set[str], list[str]]:
    """Separate options from operands.

    ``allowed`` lists the letters of supported short options. Options
    may be bundled (``-la``) and may follow operands; ``--`` ends the
    options. Raises UsageError for an unknown option.
    """
    flags: set[str] = set()
    operands: list[str] = []
    options_ended = False
    for arg in args:
        if options_ended or not is_option(arg):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_ended = True
        elif arg.startswith(END_OF_OPTIONS):
            raise UsageError(f"{command}: unrecognized option '{arg}'")
        else:
            flags.update(check_letters(command, arg, allowed))
    return flags, operands


def check_letters(command: str, arg: str, allowed: str) -> str:
    """Return the letters of a bundle of short options."""
    letters = arg[len(OPTION_PREFIX):]
    for letter in letters:
        if letter not in allowed:
            raise UsageError(f"{command}: invalid option -- '{letter}'")
    return letters
