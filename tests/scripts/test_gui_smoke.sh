#!/bin/sh
# The window opens, runs the startup script and closes on exit.
. "$(dirname "$0")/lib.sh"

if [ -z "$DISPLAY" ]; then
    if ! command -v xvfb-run >/dev/null 2>&1; then
        echo "  skip: no display and no xvfb-run"
        exit 0
    fi
    EMU="xvfb-run -a $EMU"
fi
OUTPUT=$($EMU --script "$STARTUP/stage2_exit.emu" 2>&1)
STATUS=$?
if printf '%s' "$OUTPUT" | grep -q "GUI is unavailable"; then
    echo "  skip: GUI is unavailable (no tkinter)"
    exit 0
fi
expect_status 0
expect_output "[debug]   no-gui = False"
finish
