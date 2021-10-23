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
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#
clear

echo "Start"
cd dist

export EXPORT_PATH="`pwd`"
export PRODUCT_NAME="PyGitIssueClone"
export APP_PATH="$EXPORT_PATH/$PRODUCT_NAME.app"
export ZIP_PATH="$EXPORT_PATH/$PRODUCT_NAME.zip"

echo Clean up in case of restart on failure
rm -rfv "${PRODUCT_NAME}.zip"

echo Create a ZIP archive suitable for notarization.
/usr/bin/ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"

# for Xcode 13
echo Call Apple for notary service
xcrun notarytool submit "${PRODUCT_NAME}.zip" --keychain-profile "APP_PASSWORD" --wait

#  Not needed -- single member                  --asc-provider <ProviderShortname>
