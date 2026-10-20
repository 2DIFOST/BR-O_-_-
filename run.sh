#!/bin/sh
ROOT=$(cd "$(dirname "$0")" && pwd)
PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}" \
    exec "${PYTHON:-python3}" -m shellemu "$@"
