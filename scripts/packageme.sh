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
        # python3 setup.py py2app -A --iconfile src/org/pyut/resources/img/Pyut.icns
        python3 setup.py py2app -A
else
    if [[ ${1} = 'deploy' ]] ; then
            echo "create deployable binary"
            rm -rf build dist
            # python3 setup.py py2app packages=wx,PyGithub,todoist-python --iconfile src/org/pyut/resources/img/Pyut.icns
            python3 setup.py py2app --packages=wx,github,todoist
    else
        echo "Unknown command line arguments"
    fi
# rm -rf src/UNKNOWN.egg-info
fi
