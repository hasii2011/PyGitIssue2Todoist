#!/usr/bin/env bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

rm -rf dist build

rm -rf PyGitIssueClone.egg-info
rm -rf .eggs
