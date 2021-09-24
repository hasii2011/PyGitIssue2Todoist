#!/usr/bin/env bash

#
#  assumes xcode is installed
#  assumes I added an entry APP_PASSWORD to my keychain
#
clear


xcrun altool --notarization-history 0 -p "@keychain:APP_PASSWORD"
