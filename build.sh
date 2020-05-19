#!/usr/bin/env bash
# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GNU General Public License v3.0 only

# Uncomment this with your own keystore properties file
# . ~/.keystores/props-myapps
# Properties file template:
# keystoreFile=
# keystorePassword=
# keystoreAlias=
# keyPassword=

if [[ ! $1 == "SmartPack" ]]; then
    sed -i 's/org.gradle.jvmargs=.*//' gradle.properties
    echo "org.gradle.jvmargs=-Xmx3g -XX:MaxPermSize=2048m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8" >> gradle.properties
fi

if [[ $1 == "LibreraPro" ]] ;then
    touch ~/.gradle/gradle.properties
    echo "RELEASE_STORE_FILE=~/.keystores/myapps.pkcs12" >> ~/.gradle/gradle.properties
    echo "RELEASE_STORE_PASSWORD=$keystorePassword" >> ~/.gradle/gradle.properties
    echo "RELEASE_KEY_ALIAS=$keystoreAlias" >> ~/.gradle/gradle.properties
    echo "RELEASE_KEY_PASSWORD=$keystorePassword" >> ~/.gradle/gradle.properties
    bash Builder/link_to_mupdf_1.16.1.sh
    ./gradlew clean assembleFdroid || echo "Failed"
    rm ~/.gradle/gradle.properties
elif [[ $1 == "AntennaPod" ]]; then
    echo "releaseStoreFile=$keystoreFile" >> gradle.properties
    echo "releaseStorePassword=$keystorePassword" >> gradle.properties
    echo "releaseKeyAlias=$keystoreAlias" >> gradle.properties
    echo "releaseKeyPassword=$keystorePassword" >> gradle.properties
    ./gradlew clean assembleRelease || echo "Failed"
elif [[ $1 == "SmartPack" ]]; then
    ./gradlew clean assembleRelease || echo "Failed"
else
    ./gradlew clean assembleRelease || echo "Failed"
fi
