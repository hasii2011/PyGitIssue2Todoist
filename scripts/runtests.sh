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

./scripts/cleanup.sh

cd -  > /dev/null 2>&1


echo "Exit with status: ${status}"
exit ${status}

