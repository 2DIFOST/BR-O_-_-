#!/bin/sh
# An unknown parameter is rejected with the usage message.
. "$(dirname "$0")/lib.sh"

run_emu '' --no-gui --unknown
expect_status 2
expect_output "usage: shellemu"
finish
