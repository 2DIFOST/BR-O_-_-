"""Loading of a VFS from an XML file.

The file is only read; its content is never unpacked or changed on
the disk, the whole VFS lives in memory.

Format::

    <vfs>
      <dir name="docs">
        <file name="a.txt">text</file>
        <file name="b.bin" encoding="base64">AAEC/w==</file>
      </dir>
    </vfs>
"""
import base64
import binascii
import os
from xml.etree import ElementTree as xml_tree

from .errors import VfsError, VfsFormatError
from .vfs import ERR_IS_DIR, Directory, File, Node, Vfs

ROOT_TAG = "vfs"
TAG_DIR = "dir"
TAG_FILE = "file"
ENCODING_TEXT = "text"
ENCODING_BASE64 = "base64"
FORBIDDEN_NAMES = (".", "..")
SEPARATOR = "/"


def check_name(element: xml_tree.Element) -> str:
    """Return the name of an element after checking that it is valid."""
    name = element.get("name")
    if not name:
        raise VfsFormatError(f"<{element.tag}> without a name")
    bad = (name in FORBIDDEN_NAMES or SEPARATOR in name
           or any(char.isspace() for char in name))
    if bad:
        raise VfsFormatError(f"invalid name '{name}'")
    return name


def decode_base64(text: str, name: str) -> bytes:
    """Decode the base64 content of the file ``name``."""
    try:
        return base64.b64decode("".join(text.split()), validate=True)
    except binascii.Error as error:
        raise VfsFormatError(
            f"file '{name}' has invalid base64 data"
        ) from error


def read_file_data(element: xml_tree.Element, name: str) -> bytes:
    """Return the bytes of a file described by ``element``."""
    if len(element):
        raise VfsFormatError(f"file '{name}' must not contain elements")
    text = element.text or ""
    encoding = element.get("encoding", ENCODING_TEXT)
    match encoding:
        case "text":
            return text.encode("utf-8")
        case "base64":
            return decode_base64(text, name)
        case _:
            raise VfsFormatError(
                f"file '{name}' has unknown encoding '{encoding}'"
            )


def build_node(element: xml_tree.Element) -> Node:
    """Create a file or a directory (with content) from an element."""
    match element.tag:
        case "dir":
            node = Directory(check_name(element))
            fill_directory(node, element)
        case "file":
            name = check_name(element)
            node = File(name, read_file_data(element, name))
        case _:
            raise VfsFormatError(f"unknown element <{element.tag}>")
    return node


def fill_directory(directory: Directory, element: xml_tree.Element) -> None:
    """Create the children of ``directory`` from sub-elements."""
    if (element.text or "").strip():
        raise VfsFormatError(
            f"directory '{directory.path}' must not contain text"
        )
    for child in element:
        node = build_node(child)
        if node.name in directory.children:
            raise VfsFormatError(
                f"duplicate name '{node.name}' in '{directory.path}'"
            )
        directory.add(node)


def build_root(element: xml_tree.Element) -> Directory:
    """Create the root directory from the ``<vfs>`` element."""
    if element.tag != ROOT_TAG:
        raise VfsFormatError(
            f"root element must be <{ROOT_TAG}>, found <{element.tag}>"
        )
    root = Directory()
    fill_directory(root, element)
    return root


def read_bytes(path: str) -> bytes:
    """Read the XML file; report problems as VfsError."""
    if os.path.isdir(path):
        raise VfsError(f"cannot load VFS '{path}': {ERR_IS_DIR}")
    try:
        with open(path, "rb") as file:
            return file.read()
    except OSError as error:
        raise VfsError(
            f"cannot load VFS '{path}': {error.strerror}"
        ) from error


def load_vfs(path: str) -> Vfs:
    """Load a VFS from an XML file into memory.

    Raises VfsError if the file is missing, is not well-formed XML or
    does not describe a valid file system.
    """
    data = read_bytes(path)
    try:
        root = build_root(xml_tree.fromstring(data))
    except xml_tree.ParseError as error:
        raise VfsError(
            f"cannot load VFS '{path}': invalid XML ({error})"
        ) from error
    except VfsFormatError as error:
        raise VfsError(
            f"cannot load VFS '{path}': invalid format: {error}"
        ) from error
    return Vfs(root, path)
