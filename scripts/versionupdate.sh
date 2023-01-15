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

REPO_SLUG='hasii2011/pygitissue2todoist'
VERSION_FILE='pygitissue2todoist/resources/version.txt'

traviscli  --repo-slug ${REPO_SLUG} --file ${VERSION_FILE}

PACKAGE_LIST='./pygitissue2todoist/resources/packages.txt'
PACKAGE_VERSIONS='./pygitissue2todoist/resources/packageversions.txt'

pkgversions -p ${PACKAGE_LIST} -o ${PACKAGE_VERSIONS}
