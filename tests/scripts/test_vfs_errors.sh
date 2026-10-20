#!/bin/sh
# VFS loading errors are reported; the emulator stays usable.
. "$(dirname "$0")/lib.sh"

check_error() {
    echo "-- $1"
    run_emu 'vfs-info\nexit\n' --no-gui --vfs "$2"
    expect_status 1
    expect_output "vfs error: cannot load VFS '$2': $3"
    expect_output "source:      (empty, built-in)"
}

check_error "file not found" /no/such/vfs.xml "No such file or directory"
check_error "not XML" "$DATA/not_xml.xml" "invalid XML"
check_error "unclosed tag" "$DATA/unclosed.xml" "invalid XML"
check_error "wrong root" "$DATA/wrong_root.xml" \
    "invalid format: root element must be <vfs>"
check_error "unknown element" "$DATA/unknown_element.xml" \
    "invalid format: unknown element <symlink>"
check_error "bad base64" "$DATA/bad_base64.xml" \
    "invalid format: file 'a' has invalid base64 data"
check_error "unknown encoding" "$DATA/unknown_encoding.xml" \
    "invalid format: file 'a' has unknown encoding 'rot13'"
check_error "no name" "$DATA/no_name.xml" \
    "invalid format: <file> without a name"
check_error "bad name" "$DATA/bad_name.xml" "invalid format: invalid name"
check_error "duplicate" "$DATA/duplicate.xml" \
    "invalid format: duplicate name 'a' in '/'"
check_error "directory instead of file" "$ROOT" "Is a directory"

echo "-- the startup script is skipped after a VFS error"
run_emu '' --no-gui --vfs /no/such/vfs.xml --script "$STARTUP/stage3_vfs.emu"
expect_status 1
expect_output "startup script skipped, the VFS was not loaded"
expect_no_output "directories:"
finish
