#!/bin/sh
# All parameters together.
. "$(dirname "$0")/lib.sh"

run_emu '' --no-gui --vfs /some/vfs.xml --script "$STARTUP/stage2_exit.emu"
expect_status 0
expect_output "[debug]   vfs    = /some/vfs.xml"
expect_output "[debug]   script = $STARTUP/stage2_exit.emu"
expect_output "[debug]   no-gui = True"
expect_output "cd src"
finish
