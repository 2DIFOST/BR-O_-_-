#!/bin/sh
# Common helpers for the real-OS test scripts.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
EMU="$ROOT/run.sh"
STARTUP="$ROOT/examples/startup"
VFS="$ROOT/examples/vfs"
DATA="$ROOT/tests/data"
OUTPUT=""
STATUS=0
FAILED=0

# run_emu STDIN ARGS...: run the emulator, keep output and exit status.
run_emu() {
    input=$1
    shift
    OUTPUT=$(printf '%b' "$input" | "$EMU" "$@" 2>&1)
    STATUS=$?
}

pass() {
    printf '  ok:   %s\n' "$1"
}

fail() {
    printf '  FAIL: %s\n' "$1"
    FAILED=1
}

expect_output() {
    if printf '%s\n' "$OUTPUT" | grep -qF -- "$1"; then
        pass "output contains: $1"
    else
        fail "output must contain: $1"
    fi
}

expect_no_output() {
    if printf '%s\n' "$OUTPUT" | grep -qF -- "$1"; then
        fail "output must not contain: $1"
    else
        pass "output does not contain: $1"
    fi
}

expect_status() {
    if [ "$STATUS" -eq "$1" ]; then
        pass "exit status is $1"
    else
        fail "exit status is $STATUS, expected $1"
    fi
}

# finish: print the output on failure and exit with the result.
finish() {
    if [ "$FAILED" -ne 0 ]; then
        printf -- '--- emulator output ---\n%s\n-----------------------\n' \
            "$OUTPUT"
        exit 1
    fi
    exit 0
}
