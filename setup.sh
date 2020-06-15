#!/usr/bin/env bash
# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GPL-3.0-only

CUR_DIR = $(pwd)
CHROMEDRIVER_VER='83.0.4103.39'
CHROMEDIRVER_BASE_URL='https://chromedriver.storage.googleapis.com/index.html?path=${CHROMEDRIVER_VER}/chromedriver'
PLATFORM=$(uname -s)

echo "Setting up dependencies"

if [[ ! -d bin ]]
    mkdir bin
fi

echo "Getting ChromeDriver"

if [[ $PLATFORM == "Linux "]]; then
    wget ${CHROME_BASE_URL}_linux64.zip -o 'bin/chromedriver.zip'
    unzip bin/chromedriver.zip
elif [[ $PLATFORM == 'FreeBSD']]; then
    wget ${CHROME_BASE_URL}_mac64.zip -o 'bin/chromedriver.zip'
    unzip bin/chromedriver.zip
fi

export PATH=${CUR_DIR}/bin:$PATH

echo "Please add ${CUR_DIR}/bin to your $PATH"
echo "All done"
wait 3 && clear