#!/usr/bin/env bash

#
#  assumes xcode 13 is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#
function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "codesign" ]]; then
        cd ../..
    fi
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
