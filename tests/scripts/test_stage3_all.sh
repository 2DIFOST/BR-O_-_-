#!/bin/sh
# The startup script of stage 3 tests all commands and ends with an error.
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --vfs "$VFS/deep.xml" \
    --script "$STARTUP/stage3_all.emu"
expect_status 1
expect_output "directories: 9"
expect_output "\`-- util.py (32 bytes)"
expect_output "cd: too many arguments"
expect_output "line 10 failed with status 1, script stopped"
finish
