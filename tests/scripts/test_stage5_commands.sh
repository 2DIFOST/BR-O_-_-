#!/bin/sh
# Stage 5: the startup script with rm and cp (ends with an error).
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --vfs "$VFS/deep.xml" \
    --script "$STARTUP/stage5_commands.emu"
expect_status 1
expect_output "directories: 9"
expect_output "directories: 8"
expect_output "18 bin/tool.bin"
expect_output "- 34 report.txt"
expect_output "cp: -r not specified; omitting directory '/docs2'"
expect_output "line 28 failed with status 1, script stopped"
expect_no_output "never printed"
finish
