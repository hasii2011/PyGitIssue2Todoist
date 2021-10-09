
function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "codesign" ]]; then
        cd ../..
    fi
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi

}


export APP=PyGitIssueClone.app

xcrun stapler staple dist/${APP}
