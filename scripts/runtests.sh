#!/usr/bin/env bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot



python3 -m tests.TestAll $*
status=$?

cd -  > /dev/null 2>&1

./scripts/cleanup.sh

echo "Exit with status: ${status}"
exit ${status}

