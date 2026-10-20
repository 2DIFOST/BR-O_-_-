#!/bin/sh
# No parameters: the debug output says that nothing is set.
. "$(dirname "$0")/lib.sh"

run_emu 'echo a b\nfoo\nexit\n' --no-gui
expect_status 0
expect_output "[debug]   vfs    = (not set)"
expect_output "[debug]   script = (not set)"
expect_output "echo a b"
expect_output "foo: command not found"
finish
