#!/usr/bin/env bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "codesign" ]]; then
        cd ../..
    fi
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi

}

changeToProjectRoot

#
#  assumes xcode 13 is installed
#
clear

echo "Position ourselves"
cd dist

export APP="PyGitIssueClone.app"
export LOGFILE="CodeSigning.log"

# PyGitIssueClone.app/Contents/Frameworks/liblzma.5.dylib: main executable failed strict validation
# manually copy from: /usr/local/Cellar/xz/5.2.5/lib/liblzma.5.dylib
#echo "Work around bug in copying of libraries"
# https://stackoverflow.com/questions/62095338/py2app-fails-macos-signing-on-liblzma-5-dylib
export GOOD_LIB='/usr/local/Cellar/xz/5.2.5/lib/liblzma.5.dylib'
export DIR_TO_OVER_WRITE="${APP}/Contents/Frameworks"

cp -p ${GOOD_LIB} ${DIR_TO_OVER_WRITE}

#
#  Ugh code signing will be the death of me
#
rm -v PyGitIssueClone.app/Contents/Resources/lib/python3.9/todoist/.DS_Store
rm -v PyGitIssueClone.app/Contents/Resources/lib/python3.9/numpy/f2py/tests/src/assumed_shape/.f2py_f2cmap

#
# This is a real certificate - expires 21 September 2026
#
export IDENTITY="Developer ID Application: Humberto Sanchez II (NA8Z96F8V9)"
export OPTIONS="--verbose --timestamp --options=runtime "

echo "Sign frameworks"
echo "" > ${LOGFILE}
codesign --sign "${IDENTITY}" ${OPTIONS} "${APP}/Contents/Frameworks/Python.framework/Versions/3.9/Python" >> ${LOGFILE} 2>&1

echo "Sign libraries"

find "PyGitIssueClone.app" -iname '*.so' -or -iname '*.dylib' |
    while read libfile; do
        codesign --sign "${IDENTITY}" ${OPTIONS} "${libfile}" >> ${LOGFILE} 2>&1 ;
    done;

codesign --sign "${IDENTITY}" ${OPTIONS} "${APP}/Contents/MacOS/python" >> ${LOGFILE} 2>&1
codesign --sign "${IDENTITY}" ${OPTIONS} "${APP}/Contents/MacOS/PyGitIssueClone"  >> ${LOGFILE} 2>&1

