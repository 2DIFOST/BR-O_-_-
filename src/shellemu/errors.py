"""Exceptions raised by the emulator."""


class EmulatorError(Exception):
    """Base class of all expected emulator errors."""


class ScriptError(EmulatorError):
    """The startup script cannot be read."""


class GuiUnavailableError(EmulatorError):
    """The graphical window cannot be opened (no display)."""
