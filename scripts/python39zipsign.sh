#!/usr/bin/env bash
#
#  Signing the embedded .zip file is necessary because Apple code signing verification is failing
#  on them.  (Sheesh)
#
function changeToProjectRoot {

    export areHere=`basename ${PWD}`
    if [[ ${areHere} = "scripts" ]]; then
        cd ..
    fi
}

changeToProjectRoot

#
#  assumes xcode is installed
#
clear
echo "Position ourselves to sign the Python 3.9 PIL dylib files"
cd dist

export APP="PyGitIssueClone.app"
export TEMP_DIR="/tmp"
export ORIGINAL_ZIP_DIR="${APP}/Contents/Resources/lib"
export UNZIP_DIR="python39"
export ZIP_NAME="python39.zip"
export PYTHON_ZIP="${ORIGINAL_ZIP_DIR}/${ZIP_NAME}"
export PYTHON_UNZIP_DIR="${TEMP_DIR}/${UNZIP_DIR}"

#
echo "Cleanup temporary directory"
rm -rf "${TEMP_DIR}/${ZIP_NAME}"
rm -rf ${PYTHON_UNZIP_DIR}
#
echo "Get copy of unsigned zip file"
cp -p ${PYTHON_ZIP} ${TEMP_DIR}

echo "Unzip it"
/usr/bin/ditto -x -k "${TEMP_DIR}/${ZIP_NAME}" "${TEMP_DIR}/${UNZIP_DIR}"


export IDENTITY="Developer ID Application: Humberto Sanchez II (NA8Z96F8V9)"
export OPTIONS="--verbose --timestamp --options=runtime "

find "${PYTHON_UNZIP_DIR}/PIL/.dylibs" -iname '*.dylib' |
    while read libfile; do
        codesign --sign "${IDENTITY}" "${libfile}" ${OPTIONS}   >> PIL-LibSigning.log 2>&1 ;
        # codesign --sign "${IDENTITY}" "${libfile}" ${OPTIONS}
    done;


echo "Remove old temp copy zip file"
rm -vrf "${TEMP_DIR}/${ZIP_NAME}"
echo "recreate zip file"

/usr/bin/ditto -c -k "${TEMP_DIR}/${UNZIP_DIR}" "${TEMP_DIR}/${ZIP_NAME}"

echo "Move signed zip back"

cp -p "${TEMP_DIR}/${ZIP_NAME}" ${ORIGINAL_ZIP_DIR}