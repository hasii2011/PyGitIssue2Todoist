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

PACKAGE_LIST='./gittodoistclone/resources/packages.txt'
PACKAGE_VERSIONS='./gittodoistclone/resources/packageversions.txt'

pkgversions -p ${PACKAGE_LIST} -o ${PACKAGE_VERSIONS}
