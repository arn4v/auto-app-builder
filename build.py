#!/usr/bin/env python3

# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import datetime
import json
import os
import pathlib
import platform
import shlex
import shutil
import subprocess
import sys
import textwrap
import requests
from urllib.parse import urlparse

root_dir = os.getcwd()
working_dir = os.path.join(root_dir, "working")
bin_dir = os.path.join(root_dir, "bin")
out_dir = os.path.join(root_dir, "out")
apps_json = os.path.join(root_dir, "apps.json")

if os.path.isfile(apps_json) and os.stat(apps_json).st_size != 0:
    db = open(apps_json, "r")
    db_data = json.load(db)
    db.close()
elif os.path.isfile(apps_json) and os.stat(apps_json).st_size == 0:
    os.remove(apps_json)
    open(apps_json, "x")
elif os.path.isfile(apps_json) == False:
    open(apps_json, "x")


def parse_arguments():
    """
    Arguments to be passed into the script
    """
    parser = argparse.ArgumentParser(
        description="Build and sign your favourite FOSS Android Apps with your own keystore!",
    )
    parser.add_argument(
        "--build", default=None, metavar="APP", help="Builds specified app", type=str,
    )
    parser.add_argument(
        "--build-all", action="store_true", help="Builds all app specified in json",
    )
    parser.add_argument(
        "--list-all", action="store_true", help="Lists all apps in json",
    )
    parser.add_argument(
        "--add-app",
        type=str,
        nargs="?",
        const="",
        help="Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument(
        "--file",
        metavar="LOCAL_FILE",
        type=str,
        help="Takes application names from text file, finds specifics from F-Droid and stores it in a new or prexisting JSON file.",
    )
    parser.add_argument("--clean", action="store_false", help="Clean out directory.")
    return parser


args = parse_arguments().parse_args()


def setup():
    """
    Check if working directory exists and create it if it doesn't
    """
    if os.path.isdir(working_dir):
        os.chmod(working_dir, 0o755)
        shutil.rmtree(working_dir)
        os.mkdir(working_dir)
    else:
        os.mkdir(working_dir)

    if os.path.isdir(bin_dir) == False:
        os.mkdir(bin_dir)

    if os.path.isdir(out_dir) == False:
        os.mkdir(out_dir)


def check_platform():
    if platform.system() == "Windows":
        warning = textwrap.dedent(
            """\n
        ******************* WARNING ******************
        Some apps might not have gradlew.bat script,
        please consider using WSL on Windows.
        **********************************************
        """
        )
        print(warning)
        sys.exit()


def check_net():
    try:
        response = requests.get("https://www.google.com/", timeout=10)
        return True
    except:
        return False


def info_from_user(url=""):
    if url == "":
        url = input("Please enter repository URL: ").strip()
    else:
        url = url.strip()
    url_parser(url)


def from_file(f):
    f = os.path.join(os.getcwd(), f)
    if os.path.isfile(f) == False:
        print("Specified file doesn't exist, exiting...")
        sys.exit()

    app_list = open(f, "r").readlines()
    for app in app_list:
        app = app.strip()
        url_parser(app, True)


def url_parser(url, loop=False):
    url = urlparse(url)

    if url.netloc == "":
        name = (
            (
                url.path.replace("/", "", 1)[::-1].replace("/", "", 1)[::-1]
                if (url.path.replace("/", "", 1)[-1] == "/")
                else url.path.replace("/", "", 1)
            )
            .split("/")[1]
            .lower()
        )
        repo = url.path.replace("github.com/", "")
        remote = url.path.split("/")[0].replace(".com", "")
    else:
        name = (
            (
                url.path.replace("/", "", 1)[::-1].replace("/", "", 1)[::-1]
                if (url.path.replace("/", "", 1)[-1] == "/")
                else url.path.replace("/", "", 1)
            )
            .split("/")[1]
            .lower()
        )
        repo = (
            url.path.replace("/", "", 1)[::-1].replace("/", "", 1)[::-1]
            if (url.path.replace("/", "", 1)[-1] == "/")
            else url.path.replace("/", "", 1)
        )
        remote = url.netloc.replace(" ", "").replace(".com", "")

    branch = "master"

    parse_to_json(name, repo, branch)


def parse_to_json(name, repo, branch, remote="github"):
    new_app = dict()
    attrs_list = list()
    attrs_dict = dict()

    new_app["app"] = name
    attrs_dict["repository"] = repo
    attrs_dict["branch"] = branch
    attrs_dict["remote"] = remote

    attrs_list.append(attrs_dict)
    new_app[f"{name}"] = attrs_list

    if os.path.isfile(apps_json) and os.stat(apps_json).st_size != 0:
        apps = []

        for item in db_data:
            apps.append(item["app"])

        if name not in apps:
            db = open(apps_json, "w")
            db_data.append(new_app)
            db.write(json.dumps(db_data, indent=2))
        else:
            print(f"{name} already exists in db")
    else:
        with open(apps_json, "w") as db:
            final_list = [new_app]
            db.write(json.dumps(final_list, indent=2))


def get_info_from_json(name):
    for item in db_data:
        if item["app"] == name:
            repo = item[name][0]["repository"]
            branch = item[name][0]["branch"]
            remote = item[name][0]["remote"]
            return (repo, branch, remote)
        else:
            continue


def get_tag(repo):
    gh_tag = f"https://api.github.com/repos/{repo}/releases/latest"
    latest_tag = requests.get(gh_tag).json()["tag_name"]
    return latest_tag


def dl_gh_source(name, repo, latest_tag):
    tarball_name = os.path.join(working_dir, f"{name}.tar.gz")
    gh_dl = f"https://github.com/{repo}/archive/{latest_tag}.tar.gz"

    tarball = requests.get(gh_dl)
    tarball.raise_for_status()

    with open(tarball_name, "wb") as handle:
        for block in tarball.iter_content(1024):
            handle.write(block)
        handle.close()

    shutil.unpack_archive(
        filename=f"{working_dir}/{name}.tar.gz",
        extract_dir=f"{working_dir}",
        format="gztar",
    )

    os.remove(f"{working_dir}/{name}.tar.gz")
    os.chdir(root_dir)


def clone(name, repo, branch, remote):
    if remote == "gitlab":
        clone_url = "git://gitlab.com" + repo
    elif remote == "bitbucket":
        clone_url = "git://bitbucket.com" + repo
    elif remote == "other":
        clone_url = repo

    latest_tag = get_tag(repo).replace("v", "", 1)
    app_working_dir = os.path.join(working_dir, f"{name}-{latest_tag}")
    clonecmd = f"git clone {clone_url} -b {branch} --depth 1 {app_working_dir}"
    os.system(clonecmd)


def build(single, name, repo="", branch="", remote=""):
    setup()

    print(f"Fetching {name} information from db...\n")
    if single:
        repo, branch, remote = get_info_from_json(name)

    latest_tag = get_tag(repo)
    app_out_dir = os.path.join(out_dir, f"{name}-{latest_tag}")

    try:
        if len(os.listdir(app_out_dir)) > 0:
            print(f"Already built {name}, skipping...\n")
    except:
        if remote == "github":
            print("Download source from GitHub...\n")
            dl_gh_source(name, repo, latest_tag)
        elif remote == "gitlab":
            print("Download source from Gitlab...\n")
            clone(name, repo, branch, remote)

        app_working_dir = os.path.join(working_dir, os.listdir(working_dir)[0])

        os.chdir(app_working_dir)

        print(f"Building {name}...\n")
        try:
            subprocess.check_call(shlex.split("./gradlew clean build"))
            apk_loc = copy_build(name, latest_tag)
            if single:
                print(f"Build successful for {name}\nFind APK at {apk_loc}")
        except:
            if single:
                print(f"Build failed for {name}, exiting...\n")


def copy_build(name, latest_tag):
    date = datetime.date.today()
    app_out_dir = os.path.join(out_dir, f"{name}-{latest_tag}")
    unsigned_apk_name = f"{name}-{latest_tag}-unsigned.apk"
    dest = os.path.join(app_out_dir, unsigned_apk_name)
    os.mkdir(app_out_dir)
    releaseapk = str(list(pathlib.Path(working_dir).rglob("*release*.apk"))[0])
    shutil.copyfile(releaseapk, dest)
    return dest


def list_all():
    for item in db_data:
        name = item["app"]
        print(name)


def build_all():

    for item in db_data:
        name = item["app"]
        repo = item[name][0]["repository"]
        branch = item[name][0]["branch"]
        remote = item[name][0]["remote"]
        try:
            build(False, name, repo, branch, remote)
        except:
            print(f"Build failed for {name}, continuing...\n")


def main():
    if len(sys.argv) < 2:
        parse_arguments().print_usage()
        sys.exit(1)
    else:
        if args.add_app == "" and args.file != None:
            from_file(args.file)
        elif len(args.add_app) == 0 or args.add_app != 0:
            if len(args.add_app) > 0:
                info_from_user(args.add_app)
            else:
                info_from_user()

        if args.list_all == True:
            list_all()

        if args.build is not None:
            build(True, args.build)

        if args.build_all is not False:
            build_all()


if __name__ == "__main__":
    check_platform()

    if check_net() == False:
        print("Please check your internet connection and try again.")
        sys.exit()

    main()
