"""Parser of the command line."""


def parse_line(line: str) -> list[str]:
    """Split an input line into the command name and its arguments.

    The parser is deliberately simple: words are separated by
    whitespace, there are no quotes or substitutions.
    """
    return line.split()
