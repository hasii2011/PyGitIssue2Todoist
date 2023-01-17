#!/usr/local/bin/bash

function changeToProjectRoot {

    areHere=$(basename "${PWD}")
    export areHere
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
            echo "Create deployable binary"
            rm -rf build dist
            python -O setup.py py2app --packages=charset_normalizer --iconfile pygitissue2todoist/resources/BaseLogoV2.icns
    else
        echo "Unknown command line arguments"
    fi
fi
