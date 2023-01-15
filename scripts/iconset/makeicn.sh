#!/usr/bin/env bash
#
#
#  The generated .icns file should be copied to pygitissue2todoist/resources/
#
#  The file BaseLogo.iconset/icon_512x512@2x.png is reduced to 33% of the original size
#
#
ICON_SET_DIR='BaseLogo.iconset'
ICON_IMAGE='BaseLogo-512-Rounded.png'

mkdir ${ICON_SET_DIR}

sips -z 16 16     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_16x16.png
sips -z 32 32     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_16x16@2x.png

sips -z 32 32     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_32x32.png
sips -z 64 64     ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_32x32@2x.png

sips -z 128 128 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_128x128.png
sips -z 256 256 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_128x128@2x.png

sips -z 256 256 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_256x256.png
sips -z 512 512 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_256x256@2x.png

sips -z 512 512 ${ICON_IMAGE} --out ${ICON_SET_DIR}/icon_512x512.png


cp ${ICON_IMAGE} ${ICON_SET_DIR}/icon_512x512@2x.png

iconutil -c icns ${ICON_SET_DIR}

# rm -rf ${ICON_SET_DIR}
