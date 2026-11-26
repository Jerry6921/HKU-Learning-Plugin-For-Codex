#!/bin/sh
set -eu

program_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
runtime_dir=${HIQS_PLUGIN_RUNTIME_DIR:-"$HOME/Library/Application Support/HIQS Course Mastery/0.2.0"}
python=${HIQS_PLUGIN_PYTHON:-"$runtime_dir/venv/bin/python"}

if [ "${1:-}" = "--setup" ]; then
    shift
    if [ "$#" -gt 1 ]; then
        printf '%s\n' 'Usage: run-hiqs.sh --setup [python3]' >&2
        exit 2
    fi
    "${1:-python3}" -m venv "$runtime_dir/venv"
    "$runtime_dir/venv/bin/python" -m pip install \
        --constraint "$program_root/requirements.lock" \
        "$program_root"
    exit
fi

if [ ! -x "$python" ]; then
    printf 'HIQS runtime missing. Run: /bin/sh "%s" --setup\n' "$0" >&2
    exit 1
fi

export PYTHONPATH="$program_root/src"
export PYTHONDONTWRITEBYTECODE=1
exec "$python" -m hsas.mcp "$@"
