"""Commands that work with the content of files: ``wc``."""
from dataclasses import dataclass

from ..errors import PathError, UsageError
from ..response import Response
from ..vfs import ERR_IS_DIR, File
from .options import split_options

WC_OPTIONS = "lwc"
MIN_OPERANDS_FOR_TOTAL = 2
SINGLE = 1


@dataclass
class Row:
    """Counters of one file: the selected values and the file size."""

    counts: list[int]
    size: int
    name: str


def count_file(data: bytes, letters: str) -> list[int]:
    """Return the requested counters (l, w, c) for the content."""
    values = {
        "l": data.count(b"\n"),
        "w": len(data.split()),
        "c": len(data),
    }
    return [values[letter] for letter in letters]


def read_row(shell, path: str, letters: str) -> Row | str:
    """Count one file; return an error message if it is impossible."""
    try:
        node = shell.resolve(path)
    except PathError as error:
        return f"wc: {path}: {error}"
    if not isinstance(node, File):
        return f"wc: {path}: {ERR_IS_DIR}"
    return Row(count_file(node.data, letters), node.size, path)


def total_row(rows: list[Row], letters: str) -> Row:
    """Sum the counters of all rows."""
    counts = [sum(row.counts[index] for row in rows)
              for index in range(len(letters))]
    return Row(counts, sum(row.size for row in rows), "total")


def format_row(row: Row, width: int) -> str:
    """Format the counters of a row right-aligned to ``width``."""
    numbers = [f"{count:>{width}}" for count in row.counts]
    return " ".join(numbers + [row.name])


def column_width(rows: list[Row], letters: str, operands: int) -> int:
    """Return the width of the number columns, like ``wc`` does.

    The width fits the total size of the files; a single number for a
    single file is not padded.
    """
    if len(letters) == SINGLE and operands == SINGLE:
        return 0
    return len(str(sum(row.size for row in rows)))


def parse_wc_args(args: list[str]) -> tuple[str, list[str]]:
    """Return the selected counters (letters) and the file operands.

    Raises UsageError for an unknown option or a missing operand.
    """
    flags, paths = split_options("wc", args, WC_OPTIONS)
    if not paths:
        raise UsageError("wc: missing file operand")
    letters = "".join(c for c in WC_OPTIONS if c in flags)
    return letters or WC_OPTIONS, paths


def print_rows(
    response: Response, items: list[Row | str], letters: str
) -> None:
    """Print the counters of all files, the errors and the total."""
    rows = [item for item in items if isinstance(item, Row)]
    width = column_width(rows, letters, len(items))
    for item in items:
        if isinstance(item, Row):
            response.out(format_row(item, width))
        else:
            response.err(item)
    if len(items) >= MIN_OPERANDS_FOR_TOTAL:
        response.out(format_row(total_row(rows, letters), width))


def cmd_wc(shell, args: list[str]) -> Response:
    """Count lines (-l), words (-w) and bytes (-c) of files."""
    response = Response()
    try:
        letters, paths = parse_wc_args(args)
    except UsageError as error:
        response.err(str(error))
        return response
    items = [read_row(shell, path, letters) for path in paths]
    print_rows(response, items, letters)
    return response
