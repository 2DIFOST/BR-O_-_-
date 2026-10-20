"""Parser of the command line."""

COMMENT_PREFIX = "#"


def parse_line(line: str) -> list[str]:
    """Split an input line into the command name and its arguments.

    The parser is deliberately simple: words are separated by
    whitespace, there are no quotes or substitutions. A line that
    starts with ``#`` is a comment and gives no words.
    """
    if line.lstrip().startswith(COMMENT_PREFIX):
        return []
    return line.split()
