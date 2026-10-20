#!/bin/sh
# --vfs: the path is accepted and printed in the debug output.
. "$(dirname "$0")/lib.sh"

run_emu 'exit\n' --no-gui --vfs /some/place/vfs.xml
expect_status 0
expect_output "[debug]   vfs    = /some/place/vfs.xml"
finish
