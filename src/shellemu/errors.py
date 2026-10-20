"""Exceptions raised by the emulator."""


class EmulatorError(Exception):
    """Base class of all expected emulator errors."""


class ScriptError(EmulatorError):
    """The startup script cannot be read."""


class GuiUnavailableError(EmulatorError):
    """The graphical window cannot be opened (no display)."""


class VfsError(EmulatorError):
    """The virtual file system cannot be loaded."""


class VfsFormatError(VfsError):
    """The XML file does not describe a valid virtual file system."""
