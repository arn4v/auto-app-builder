#!/usr/bin/env bash
root_dir=$(pwd)
working_dir=$root_dir/apps
app_list=$root_dir/apps.json

get_release_info() {
    curl --silent "https://api.github.com/repos/$1/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")'
}

try() {
    [[ $- = *e* ]]; SAVED_OPT_E=$?
    set +e
}

catch() {
    export ex_code=$?
    (( $SAVED_OPT_E )) && set +e
    return $ex_code
}

echo "Root Directory: $root_dir"
echo "Working Directory: $working_dir"
printf "Building:\n$(cat $app_list | jq -r .[].app)"
echo " "

for app in $(cat $app_list | jq -r .[].app); do
    try
    apprepo=$(cat $app_list | jq -r .[].$app[]?.repository | head -n 1)
    appbranch=$(cat $app_list | jq -r .[].$app[]?.branch | head -n 1)
    tag=$(get_release_info $apprepo)
    if [[ ! -d out ]]; then mkdir out; fi
    if [[ ! -f .tags.ini ]]; then
	touch .tags.ini
    fi
    if [[ $(cat .tags.ini | grep $app | sed "s/$app:.*/$app/") == $app ]]; then
    if [[ -f $(ls $root_dir/out/$app-$tag-*.apk) ]]; then
#    if [[ $(cat .tags.ini | grep $app | sed "s/$app://") == $tag ]]; then
	echo "Already built ${app} with the tag: ${tag}"
	continue
    else
	echo "App: $app with release tag: $tag has not been built, building"
    fi
    else
        echo "${app}:${tag}" >> .tags.ini
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
	for appfile in $(find $working_dir/ -type f -name '*unsigned*apk'); do mv -- $appfile $root_dir/out/"$app-$tag-$(date +%Y%m%d_%H%M)-$appfile"; done
	killall -9 java && pkill -f '.*GradleDaemon.*'
    fi
done