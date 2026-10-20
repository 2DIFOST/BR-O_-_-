#!/bin/sh
# --vfs: the path is accepted, printed and the VFS is loaded.
. "$(dirname "$0")/lib.sh"

run_emu 'vfs-info\nexit\n' --no-gui --vfs "$VFS/minimal.xml"
expect_status 0
expect_output "[debug]   vfs    = $VFS/minimal.xml"
expect_output "source:      $VFS/minimal.xml"
expect_no_output "vfs error"
finish
