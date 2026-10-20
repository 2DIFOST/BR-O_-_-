"""History of entered commands (navigated with the Up/Down keys)."""


class History:
    """Ordered list of entered lines with a movable cursor."""

    def __init__(self) -> None:
        """Create an empty history."""
        self.items: list[str] = []
        self.index = 0

    def add(self, line: str) -> None:
        """Remember a non-empty line and move the cursor to the end."""
        if line:
            self.items.append(line)
        self.index = len(self.items)

    def previous(self) -> str:
        """Move one entry back and return it."""
        self.index = max(self.index - 1, 0)
        return self.current()

    def following(self) -> str:
        """Move one entry forward and return it (empty at the end)."""
        self.index = min(self.index + 1, len(self.items))
        return self.current()

    def current(self) -> str:
        """Return the entry under the cursor or an empty string."""
        if self.index < len(self.items):
            return self.items[self.index]
        return ""
