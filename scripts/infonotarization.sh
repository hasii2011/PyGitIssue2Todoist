#!/usr/bin/env bash

#
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#
clear

#xcrun altool --notarization-info $1 -p "@keychain:APP_PASSWORD"

xcrun notarytool log $1 --keychain-profile "APP_PASSWORD" developer_log.json
#