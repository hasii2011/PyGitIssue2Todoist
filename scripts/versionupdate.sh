#!/usr/bin/env bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi

    if [[ ${areHere} = "src" ]]; then
        cd ..
    fi
}

changeToProjectRoot

REPO_SLUG='hasii2011/gittodoistclone'
VERSION_FILE='gittodoistclone/resources/version.txt'

traviscli  --repo-slug ${REPO_SLUG} --file ${VERSION_FILE}

STATUS=$?

exit ${STATUS}
