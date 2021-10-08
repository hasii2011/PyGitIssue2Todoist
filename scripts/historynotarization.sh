#!/usr/bin/env bash

#
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#  This command line is pre-Xcode-13

clear


xcrun altool --notarization-history 0 -p "@keychain:APP_PASSWORD"
