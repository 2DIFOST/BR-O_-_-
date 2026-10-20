#!/bin/sh
# The window opens, loads a VFS, runs the script and closes on exit.
. "$(dirname "$0")/lib.sh"

if [ -z "$DISPLAY" ]; then
    if ! command -v xvfb-run >/dev/null 2>&1; then
        echo "  skip: no display and no xvfb-run"
        exit 0
    fi
    EMU="xvfb-run -a $EMU"
fi
OUTPUT=$($EMU --vfs "$VFS/deep.xml" --script "$STARTUP/stage3_vfs.emu" 2>&1)
STATUS=$?
if printf '%s' "$OUTPUT" | grep -q "GUI is unavailable"; then
    echo "  skip: GUI is unavailable (no tkinter)"
    exit 0
fi
expect_status 0
expect_output "[debug]   no-gui = False"
expect_output "[debug]   vfs    = $VFS/deep.xml"
finish
