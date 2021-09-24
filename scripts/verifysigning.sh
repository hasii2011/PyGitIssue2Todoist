#!/usr/bin/env bash

#
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}
#
#  assumes xcode is installed
#

changeToProjectRoot

clear

spctl -vvvv --assess --type exec dist/PyGitIssueClone.app
