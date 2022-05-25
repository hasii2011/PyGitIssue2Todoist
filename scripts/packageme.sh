#!/usr/local/bin/bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

#
#  Assumes python 3 is on PATH
#
clear

if [[ $# -eq 0 ]] ; then
        echo "in alias mode"
        rm -rf build dist
        python setup.py py2app -A
else
    if [[ ${1} = 'deploy' ]] ; then
            echo "create deployable binary"
            rm -rf build dist
            python -O setup.py py2app --packages=wx,github,todoist --iconfile gittodoistclone/resources/BaseLogo.icns
    else
        echo "Unknown command line arguments"
    fi
fi
