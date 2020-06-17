#!/usr/bin/env python3

# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import datetime
import glob
import json
import os
import platform
import requests
import shutil
import subprocess
import sys
import textwrap
import urllib.request

# from bs4 import BeautifulSoup
from pathlib import Path

root_dir = os.getcwd()
working_dir = f"{root_dir}/working"
bin_dir = f"{root_dir}/bin"
out_dir = f"{root_dir}/out"
apps_json = f"{root_dir}/apps.json"

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


def parse_arguments():
    """
    Arguments to be passed into the script
    """
    parser = argparse.ArgumentParser(
        description="Build and sign your favourite FOSS Android Apps with your own keystore!",
        prefix_chars="--",
    )
    parser.add_argument(
        "--build", default=None, metavar="APP", help="Builds specified app", type=str,
    )
    parser.add_argument(
        "--build-all", action="store_true", help="Builds all app specified in json",
    )
    parser.add_argument(
        "--fdroid",
        action="store_true",
        help="Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument(
        "--add-app",
        action="store_true",
        help="Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument(
        "--from-file",
        metavar='FILE',
        type=argparse.FileType("r"),
        help="Takes application names from text file, finds specifics from F-Droid and stores it in a new or prexisting JSON file.",
    )
    parser.add_argument("--clean", action="store_false", help="Clean out directory.")
    return parser


def setup():
    """
    Check if working directory exists and create it if it doesn't
    """
    if os.path.isdir(working_dir):
        os.chmod(working_dir, stat.S_IWUSR)
        shutil.rmtree(working_dir)
        # os.system(f"rm -rf {working_dir}")
        os.mkdir(working_dir)
    else:
        os.mkdir(working_dir)

    if os.path.isdir(bin_dir) == False:
        os.mkdir(bin_dir)

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir, ignore_errors=True)
        os.mkdir(out_dir)
    else:
        os.mkdir(out_dir)

    if os.path.isfile(apps_json) == False:
        with open(apps_json, "x") as db:
            db.close()


def info_from_fdroid(name):
    return "This will eventually fetch relevant information from F-Droid."


def parse_to_json(name, branch, repo):
    setup()
    new_app = {
        "app": name,
        name: [{"repository": repo, "remote": repo, "branch": branch,}],
    }
    with open(apps_json, "w+", encoding="utf-8") as db:
        dblist = db.readlines()
        dblist = dblist.append(new_app)
        db.writelines(dblist)


def info_from_user():
    print("Please enter app specifics: \n")
    name = input("Enter app name: \n").lower
    branch = input("Enter branch to use: \n").lower
    repo = input("Enter git URL \n").lower
    parse_to_json(name, branch, repo)


def get_info_from_json(name):
    db = open(apps_json, mode="r")
    db_data = json.load(db)
    db.close()
    repo = db_data[0][name][0]["repository"]
    branch = db_data[0][name][0]["branch"]
    remote = db_data[0][name][0]["remote"]
    return [repo, branch, remote]


def get_total():
    app_list = []
    db_data = json.load(open(apps_json, mode="r"))
    total = len(db_data)
    for item in total:
        app_list.append(db_data[item - 1]["app"])
    return [app_list, total]


def get_tag(repo):
    gh_tag = f"https://api.github.com/repos/{repo}/releases/latest"
    latest_tag = json.load(urllib.request.urlopen(gh_tag))
    latest_tag = latest_tag["tag_name"]
    return latest_tag


def dl_gh_source(name, repo):
    latest_tag = get_tag(repo)
    tarball_name = f"{working_dir}/{name}.tar.gz"
    gh_dl = f"https://github.com/{repo}/archive/{latest_tag}.tar.gz"
    urllib.request.urlretrieve(gh_dl, tarball_name)

    tarball = requests.get(gh_dl, stream=True)
    tarball.raise_for_status()

    with open(tarball_name, "wb") as handle:
        for block in tarball.iter_content(1024):
            handle.write(block)

    shutil.unpack_archive(
        filename=f"{working_dir}/{name}.tar.gz",
        extract_dir=f"{working_dir}",
        format="gztar",
    )

    # os.system(f"tar -xzf {tarball_name}")
    os.remove(f"{working_dir}/{name}.tar.gz")
    os.chdir(root_dir)


def dl_gitlab_source(name, repo, branch):
    app_dir = f"{working_dir}/{name}"
    clonecmd = f"git clone git://gitlab.com/{repo} -b {branch} --depth 1 {app_dir}"
    os.system(clonecmd)

def build(name):
    setup()
    repo = get_info_from_json(name)[0]
    branch = get_info_from_json(name)[1]
    remote = get_info_from_json(name)[2]
    latest_tag = get_tag(repo).replace("v", "", 1)
    app_working_dir = f"{working_dir}/{name}-{latest_tag}"
    gradlew = "./" + app_working_dir + "/gradlew"

    if remote == "github":
        dl_gh_source(name, repo)
    elif remote == "gitlab":
        dl_gitlab_source(name, repo, branch)

    # os.system(f"./{app_working_dir}/gradlew assembleRelease")
    subprocess.check_call(gradlew, "clean", "build")


def build_all():
    for app in get_total()[0]:
        print(f"Build {app}")
        build(app)


def main():
    args = parse_arguments().parse_args()
    if len(sys.argv) < 2:
        parse_arguments().print_usage()
        sys.exit(1)
    else:
        if args.add_app and args.fdroid and args.from_file:
            for apps in args.from_file:
                info_from_fdroid(apps)
        elif args.add_app and args.fdroid:
            info_from_fdroid(args.add_app)
        elif args.add_app:
            info_from_user()

        if args.build is not None:
            build(args.build)

        if args.build_all is not False:
            build_all()


if __name__ == "__main__":
    main()
