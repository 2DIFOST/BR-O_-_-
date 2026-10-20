#!/bin/sh
# VFS with six levels of folders and files.
. "$(dirname "$0")/lib.sh"

run_emu 'vfs-info\nvfs-tree\nexit\n' --no-gui --vfs "$VFS/deep.xml"
expect_status 0
expect_output "directories: 9"
expect_output "files:       9"
expect_output "depth:       6"
expect_output "|           \`-- emulator/"
expect_output "main.py (15 bytes)"
expect_output "idea.txt (26 bytes)"
finish
