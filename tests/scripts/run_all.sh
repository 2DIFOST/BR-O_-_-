#!/bin/sh
# Run all real-OS test scripts; exit status is non-zero on any failure.
DIR=$(cd "$(dirname "$0")" && pwd)
failed=0
for script in "$DIR"/test_*.sh; do
    echo "== $(basename "$script")"
    sh "$script" || failed=1
done
if [ "$failed" -ne 0 ]; then
    echo "SOME SCRIPTS FAILED"
    exit 1
fi
echo "ALL SCRIPTS PASSED"
