#!/bin/sh
# Minimal VFS: only the empty root directory.
. "$(dirname "$0")/lib.sh"

run_emu 'vfs-info\nvfs-tree\nexit\n' --no-gui --vfs "$VFS/minimal.xml"
expect_status 0
expect_output "directories: 0"
expect_output "files:       0"
expect_output "depth:       0"
expect_output "vfs-tree"
finish
