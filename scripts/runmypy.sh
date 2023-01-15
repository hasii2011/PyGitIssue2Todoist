#!/usr/bin/env bash

function changeToProjectRoot {

    areHere=$(basename "${PWD}")
    export areHere
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

echo "current: $(pwd)"

OPTS="--pretty --no-color-output  --show-error-context --check-untyped-defs --show-error-codes"
mypy --config-file gittodoistclone/.mypi.ini ${OPTS} gittodoistclone tests
status=$?

echo "Exit with status: ${status}"
exit ${status}

