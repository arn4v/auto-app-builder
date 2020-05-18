#!/usr/bin/env bash
# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GNU General Public License v3.0 only

root_dir=$(pwd)
working_dir=$root_dir/apps
out_dir=$root_dir/out
app_list=$root_dir/apps.json

echo "Root Directory: $root_dir"
echo "Working Directory: $working_dir"
printf "Building:\n$(cat $app_list | jq -r .[].app)"
echo " "

get_release_info() {
    curl --silent "https://api.github.com/repos/$1/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")'
}

build() {
	echo "$app:$tag" >> .tags.ini
	rm -rf $working_dir
	mkdir $working_dir && cd $working_dir
	echo "Downloading $app source"
	echo " "
	wget https://github.com/$apprepo/archive/$tag.zip
	echo "Decompressing $app source"
	echo " "
	unzip *.zip
	rm *zip
	cd $working_dir/*
	echo "sdk.dir=${ANDROID_SDK_PATH}" >> "local.properties"
	echo "Building $app with tag: $tag sources"
	echo " "
	bash $root_dir/build.sh $app
        if [[ ! -d "$out_dir/$app-$tag-$(date +%Y%m%d)" ]]; then mkdir $out_dir/$app-$tag-$(date +%Y%m%d); fi
	find $working_dir/ -iname '*unsigned*.apk' -exec mv {} $out_dir/$app-$tag-$(date +%Y%m%d) \;
        ls $out_dir/$app-$tag-$(date +%Y%m%d)/ | xargs -I {} mv {} $app-$tag-$(date +%Y%m%d_%H%M)_{}
        killall -9 java && pkill -f '.*GradleDaemon.*'
	cd $root_dir
}

for app in $(cat $app_list | jq -r .[].app); do
    apprepo=$(cat $app_list | jq -r .[].$app[]?.repository | head -n 1)
    appbranch=$(cat $app_list | jq -r .[].$app[]?.branch | head -n 1)
    tag=$(get_release_info $apprepo)
    if [[ ! -d out ]]; then mkdir out; fi
    if [[ ! -f .tags.ini ]]; then touch .tags.ini; fi
    if [[ $(cat .tags.ini | grep $app | sed "s/${app}.*/${app}/") == $app ]] && [[ $(cat .tags.ini | grep $app | sed "s/${app}://") == $tag ]] && [[ -d "$out_dir/$app-$tag-$(date +%Y%m%d)" ]] && [[ $(ls "$out_dir/$app-$tag-$(date +%Y%m%d)" | head -c1 | wc -c) -ne 0 ]]; then
        echo "Already build $app with release tag $tag sources, continuing."
        continue
    else
	if [[ $(cat .tags.ini | grep $app | head -c1 | wc -c) -ne 0 ]]; then sed -i "s/${app}.*//" .tags.ini; fi
	build
    fi
done
