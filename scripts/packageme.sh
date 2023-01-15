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
            echo "create deployable binary"
            rm -rf build dist
            # python -O setup.py py2app --packages=wx,github,todoist-api-python --iconfile pygitissue2todoist/resources/BaseLogo.icns
            python -O setup.py py2app --packages=charset_normalizer --iconfile gittodoistclone/resources/BaseLogo.icns
    else
        echo "Unknown command line arguments"
    fi
fi
