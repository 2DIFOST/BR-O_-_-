#!/bin/sh
# --script: execution stops at the first error and it is reported.
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --script "$STARTUP/stage2_error.emu"
expect_status 1
expect_output "cd: too many arguments"
expect_output "line 3 failed with status 1, script stopped"
expect_no_output "ls must-not-run"
finish
