#!/bin/sh
# VFS with several files, including a binary one (base64).
. "$(dirname "$0")/lib.sh"

run_emu 'vfs-info\nvfs-tree\nexit\n' --no-gui \
    --vfs "$VFS/several_files.xml"
expect_status 0
expect_output "directories: 0"
expect_output "files:       5"
expect_output "size:        80 bytes"
expect_output "|-- data.bin (16 bytes)"
expect_output "|-- empty.txt (0 bytes)"
expect_output "\`-- russian.txt (22 bytes)"
finish
