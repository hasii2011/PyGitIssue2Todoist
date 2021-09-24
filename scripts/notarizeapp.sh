#!/usr/bin/env bash

function changeToProjectRoot {

    export areHere=`basename ${PWD}`
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

echo "Position ourselves"
cd dist

export EXPORT_PATH="`pwd`"
export PRODUCT_NAME="PyGitIssueClone"
export APP_PATH="$EXPORT_PATH/$PRODUCT_NAME.app"
export ZIP_PATH="$EXPORT_PATH/$PRODUCT_NAME.zip"

# Create a ZIP archive suitable for notarization.
/usr/bin/ditto -c -k --keepParent "$APP_PATH" "$ZIP_PATH"

# for Xcode 13
xcrun notarytool submit "${PRODUCT_NAME}.zip" --keychain-profile "APP_PASSWORD" --wait

#  Not needed -- single member                  --asc-provider <ProviderShortname>
