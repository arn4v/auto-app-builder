#!/usr/bin/env bash

root_dir=$(pwd)
working_dir=$root_dir/apps

get_release_info() {
    curl --silent "https://api.github.com/repos/$1/tags" | jq -r '.[0].name'
}


for app in $(cat $root_dir/apps.json | jq -r .app); do
  for apprepo in $(cat $root_dir/apps.json | jq -r .repository); do
    for appbranch in $(cat $root_dir/apps.json | jq -r .branch); do
      tag=$(get_release_info $apprepo)
      if [[ ! -f tags.txt ]]; then
          echo $app=$tag >> tags.txt
      else
	if [[ $(cat tags.txt | grep $app | sed 's/$app://') == $tag ]]; then
		Already built $app with $tag tag
	else
	    mkdir -p $working_dir && cd $working_dir
	    wget https://github.com/$apprepo/archive/$tag.zip
	    unzip "${tag}.zip"
	    cd "$app-$tag"
	    echo "sdk.dir=$ANDROID_SDK_PATH" >> local.properties
	    ./gradlew clean build
	    cd $root_dir
	    rm -rf $working_dir
        fi
      fi
    done
  done
done
