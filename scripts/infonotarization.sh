#!/usr/bin/env bash
#
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#  This command line is the Xcode-13 versions
#  Single input is a notarization ID as reported by:
#
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

changeToProjectRoot

clear

xcrun notarytool log $1 --keychain-profile "APP_PASSWORD" developer_log.json
