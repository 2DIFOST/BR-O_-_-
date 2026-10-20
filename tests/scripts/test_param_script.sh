#!/bin/sh
# --script: the script is executed and shown as a dialog.
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --script "$STARTUP/stage2_ok.emu"
expect_status 0
expect_output "[debug]   script = $STARTUP/stage2_ok.emu"
expect_output "# Stage 2: startup script without errors."
expect_output "ls -l /tmp"
expect_output "cd docs"
expect_no_output "script error"
finish
