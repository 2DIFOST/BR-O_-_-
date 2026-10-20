#!/bin/sh
# All parameters together.
. "$(dirname "$0")/lib.sh"

run_emu '' --no-gui --vfs "$VFS/deep.xml" --script "$STARTUP/stage3_vfs.emu"
expect_status 0
expect_output "[debug]   vfs    = $VFS/deep.xml"
expect_output "[debug]   script = $STARTUP/stage3_vfs.emu"
expect_output "[debug]   no-gui = True"
expect_output "files:       9"
finish
