function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

#
#  xcode is installed
#
clear

echo "Position ourselves"
cd dist

export APP="PyGitIssueClone.app"

echo "Work around bug in copying of libraries"
# https://stackoverflow.com/questions/62095338/py2app-fails-macos-signing-on-liblzma-5-dylib
export GOOD_LIB='/usr/local/Cellar/xz/5.2.5/lib/liblzma.5.dylib'
export DIR_TO_OVER_WRITE="${APP}/Contents/Frameworks"

cp -p ${GOOD_LIB} ${DIR_TO_OVER_WRITE}

# This is a test certificate to make sure I sign everything
export IDENTITY="Apple Development: Humberto Sanchez II (934EG427QG)"

echo "Sign frameworks"
codesign --force --verify --verbose --sign "${IDENTITY}" "${APP}/Contents/Frameworks/Python.framework/Versions/3.9/Python"

echo "Sign libraries"

find "PyGitIssueClone.app" -iname '*.so' -or -iname '*.dylib' |
    while read libfile; do
        codesign --sign "${IDENTITY}" "${libfile}" --options=runtime --verbose   >> CodeSigning.log 2>&1 ;
    done;

codesign --sign "${IDENTITY}" --options=runtime --verbose "${APP}/Contents/MacOS/python"
codesign --sign "${IDENTITY}" --options=runtime --verbose "${APP}/Contents/MacOS/PyGitIssueClone"


# PyGitIssueClone.app/Contents/Frameworks/liblzma.5.dylib: main executable failed strict validation
# manually copy from: /usr/local/Cellar/xz/5.2.5/lib/liblzma.5.dylib
# not needed with py2app 0.26