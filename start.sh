#!/usr/bin/env bash
root_dir=$(pwd)
working_dir=$root_dir/apps
app_list=$root_dir/apps.json

get_release_info() {
#    curl --silent "https://api.github.com/repos/$1/tags" | jq -r '.[0].name'
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
printf "\nBuilding $(cat $app_list | jq -r .[].app)\n"

for app in $(cat $app_list | jq -r .[].app); do
    try
    apprepo=$(cat $app_list | jq -r .[].$app[]?.repository | head -n 1)
    appbranch=$(cat $app_list | jq -r .[].$app[]?.branch | head -n 1)
    tag=$(get_release_info $apprepo)
    if [[ ! -d out ]]; then mkdir out; fi
    if [[ ! -f tags.txt ]]; then
        echo $app:$tag >> tags.txt
    else
    if [[ $(cat tags.txt | grep $app | sed 's/$app://') == $tag ]]; then
		    Already built $app with $tag tag
    else
	rm -rf $working_dir
        mkdir $working_dir && cd $working_dir
        echo "Downloading $app source"
        wget https://github.com/$apprepo/archive/$tag.zip
        echo "Decompressing $app source"
        unzip *.zip
	rm *zip
        cd $working_dir/*
	sed -i 's/org.gradle.jvmargs=.*//' gradle.properties
        echo "sdk.dir=${ANDROID_SDK_PATH}" >> "local.properties"
        echo "org.gradle.jvmargs=-Xmx3g -XX:MaxPermSize=2048m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8" >> gradle.properties
	bash $root_dir/build.sh $app
	mv $(find $working_dir/ -type f -name '*debug*apk') $root_dir/out/$app-$tag-$(date +%Y%m%d_%H%M)-unsigned.apk
	killall -9 java && pkill -f '.*GradleDaemon.*'
    fi
   fi
done
