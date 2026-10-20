#!/bin/sh
# --script: a missing script file is reported as an error.
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --script /no/such/script.emu
expect_status 1
expect_output "script error: cannot read script '/no/such/script.emu'"
finish
