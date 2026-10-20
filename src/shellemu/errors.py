"""Exceptions raised by the emulator."""


class EmulatorError(Exception):
    """Base class of all expected emulator errors."""


class ScriptError(EmulatorError):
    """The startup script cannot be read."""


class GuiUnavailableError(EmulatorError):
    """The graphical window cannot be opened (no display)."""


class VfsError(EmulatorError):
    """The virtual file system cannot be loaded."""


class PathError(EmulatorError):
    """A path does not lead to a suitable node of the VFS.

    The message is the reason in the style of UNIX tools, e.g.
    ``No such file or directory``.
    """


class UsageError(EmulatorError):
    """A command was called incorrectly; the message is shown as is."""


class VfsFormatError(VfsError):
    """The XML file does not describe a valid virtual file system."""
