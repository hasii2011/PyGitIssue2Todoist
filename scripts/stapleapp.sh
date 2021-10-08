
function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "codsigning" ]]; then
        cd ../..
    fi
}


export APP=PyGitIssueClone.app

xcrun stapler staple dist/${APP}
