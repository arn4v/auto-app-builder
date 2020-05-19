#!/usr/bin/env bash
# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GNU General Public License v3.0 only

root_dir=$(pwd)
. "local.properties"

get_release_info() {
    curl --silent "https://api.github.com/repos/$1/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")'
}

usage()
{
  echo "Welcome to lazy builder!"
  echo "A bash script to help you automate building your favourite foss apps for your own usage, signed with your own keys!"
  echo -e "\t-h | --help"
  echo -e "\t-b | --build <app>"
  echo -e "\t-all | --build-all"
}

sign_align() {
    cd $app_out_dir
    jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -storepass $keystorePassword -keypass $keystorePassword -keystore $keystoreFile $app_file $keystoreAlias
    $ANDROID_SDK_PATH/build-tools/29.0.3/zipalign -p -v 4 $app_file_name "$app_file_name-signed"
}

add_param() {
    jq_command="jq '.[].$2 += {"${3}":"${4}"}' > $app_list"
    sh -c "$jq_command"
}

build() {
    apprepo=$(cat $app_list | jq -r .[].$app[]?.repository | head -n 1)
    appbranch=$(cat $app_list | jq -r .[].$app[]?.branch | head -n 1)
    tag=$(get_release_info $apprepo)
    app_file_name=$app-$tag-$(date +%Y%m%d)
    app_out_dir=$out_dir/$app_file_name
    app_working_dir=$working_dir/$app-$tag
    echo " "
    rm -rf $working_dir
    mkdir $working_dir && cd $working_dir
    echo "Downloading $app source"
    echo " "
    wget https://github.com/$apprepo/archive/$tag.zip -O $app-$tag.zip
    echo "Decompressing $app source"
    echo " "
    unzip "$app-$tag.zip"
    rm "$app-$tag.zip"
    echo "sdk.dir=${ANDROID_SDK_PATH}" >> "local.properties"
    echo "Building $app with tag: $tag sources"
    echo " "
    cd $working_dir/*
    bash $root_dir/app-rules.sh $app
    ./gradlew clean build
    if [[ -z $(find $app_working_dir -type -f name '*apk' | head -c 1 | wc -c) ]]; then
        rm -rf $app_out_dir
        echo "Build for $app failed, please read the error above"
        exit 1
    else
        if [[ ! -d $app_out_dir ]]; then mkdir $app_out_dir; fi
        find $app_working_dir -type f -name '*unsigned*.apk' -exec mv {} $2/ \;
        ls $app_out_dir/ | xargs -I {} mv {} $app-$tag-$(date +%Y%m%d_%H%M)_{}
        if [[ $SIGN_APP -ne 0 ]]; then sign_align; fi
        killall -9 java && pkill -f '.*GradleDaemon.*'
    fi
    cd $root_dir
}



buildall() {
    echo "Root Directory: $root_dir"
    echo "Working Directory: $working_dir"
    printf "Building:\n$(cat $app_list | jq -r .[].app)"
    for app in $(cat $app_list | jq -r .[].app); do
        apprepo=$(cat $app_list | jq -r .[].$app[]?.repository | head -n 1)
        appbranch=$(cat $app_list | jq -r .[].$app[]?.branch | head -n 1)
        tag=$(get_release_info $apprepo)
        if [[ ! -d out ]]; then mkdir out; fi
        if [[ ! -f $tags_file ]]; then touch $tags_file; fi
        if [[ $(cat $tags_file | grep $app | sed "s/${app}.*/${app}/") == $app ]] && [[ $(cat $tags_file | grep $app | sed "s/${app}://") == $tag ]] && [[ -d "$app_out_dir" ]] && [[ $(ls "$app_out_dir" | head -c1 | wc -c) -ne 0 ]]; then
            echo "Already build $app with release tag $tag sources, continuing."
            continue
        else
            if [[ $(cat $tags_file | grep $app | head -c1 | wc -c) -ne 0 ]]; then sed -i "s/${app}.*//" $tags_file; fi
            echo "$app:$tag" >> $tags_file
            build
        fi
    done
}

buildapp() {
    echo "Root Directory: $root_dir"
    echo "Working Directory: $working_dir"
    app=$@
    apprepo=$(cat $app_list | jq -r .[].$app[]?.repository | head -n 1)
    appbranch=$(cat $app_list | jq -r .[].$app[]?.branch | head -n 1)
    tag=$(get_release_info $apprepo)
    build
    exit 1
}

#addparam() {
#}


while [[ $# -gt 0 ]]
do
  key="$1"
  case $key in
    -h|--help)
      usage
      exit
      ;;
    -a|--add-aram)
      add_param $2 $3 $4
      ;;
    -s|--sign)
     SIGN_APP=1
      ;;
    -b|--build)
      app=$2
      printf "Building $app"
      buildapp $app
      ;;
    -all|--buildall)
      buildall
      ;;
    *)
    echo "Unknown parameter \"$key\""
    usage
      exit 1
      ;;
  esac
  shift
done

if [[ -z $1 ]]; then usage; fi
