#!/usr/bin/env bash

function changeToProjectRoot {

    areHere=$(basename "${PWD}")
    export areHere
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot



python3 -m tests.TestAll
status=$?

./scripts/cleanup.sh

cd -  > /dev/null 2>&1 || ! echo "No such directory"


echo "Exit with status: ${status}"
exit ${status}
