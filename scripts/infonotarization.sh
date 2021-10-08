#!/usr/bin/env bash
#
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#  This command line is the Xcode-13 versions
#  Single input is a notarization ID as reported by:
#
# xcrun notarytool history -p "APP_PASSWORD"
#
clear

xcrun notarytool log $1 --keychain-profile "APP_PASSWORD" developer_log.json
