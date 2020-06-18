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
        "--fdroid",
        action="store_true",
        help="Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument(
        "--add-app",
        type=str,
        nargs="?",
        default=None,
        help="Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument(
        "--from-file",
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

    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
        os.mkdir(out_dir)
    else:
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


def from_file():
    f = os.path.join(os.getcwd(), args.from_file)
    if os.path.isfile(f) == False:
        print("Specified file doesn't exist, exiting...")
        sys.exit()

    app_list = open(f, "r").readlines()
    for app in app_list:
        app = app.strip()
        url_parser(app, True)


def url_parser(url, loop=False):
    url = url.strip()
    base = url[::-1].replace("/", "", 1)[::-1]
    url = urlparse(url)

    if url.netloc == "":
        # When URL doesn't have https:// urlparse considers domain to be a part of the path
        # Therefore, when url.netlock is empty, delete domain from string
        name = (
            url.path.replace("/", "", 1)[::-1].replace("/", "", 1)[::-1]
            if (url.path.replace("/", "", 1)[-1] == "/")
            else url.path.replace("/", "", 1)
        ).split("/")[1]
        remote = url.path.split("/")[0].replace(".com", "")
        repo = base.split("/")[1] + base.split("/")[2]
    else:
        name = (
            url.path.replace("/", "", 1)[::-1].replace("/", "", 1)[::-1]
            if (url.path.replace("/", "", 1)[-1] == "/")
            else url.path.replace("/", "", 1)
        ).split("/")[1]
        repo = (
            url.path.replace("/", "", 1)[::-1].replace("/", "", 1)[::-1]
            if (url.path.replace("/", "", 1)[-1] == "/")
            else url.path.replace("/", "", 1)
        )
        remote = url.netloc.replace(" ", "").replace(".com", "")

    if os.path.isfile(apps_json):
        db = open(apps_json, mode="r", encoding="utf-8")
        db_data = json.load(db)
        db.close()
        if db_data[0]["app"] == name:
            print(f"{name} already exists")
        else:
            if remote == "github":
                try:
                    gh_tag = f"https://api.github.com/repos/{repo}/releases/latest"
                    branch = requests.get(gh_tag).json()["target_commitish"]
                except:
                    print(
                        "Unable to fetch default branch from GitHub, defaulting to master..."
                    )
                    branch = "master"
            else:
                if loop == False:
                    branch = input("Please enter target branch: (Default = master) ")

                    if branch == "":
                        branch = "master"
                else:
                    branch = "master"

            if remote != "github":
                parse_to_json(name, repo, branch, remote)
            else:
                parse_to_json(name, repo, branch)


# TODO: Use Selenium To Fetch Info From F-Droid
def info_from_fdroid(name):
    return "This will eventually fetch relevant information from F-Droid."


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

    if os.path.isfile(apps_json):
        db = open(apps_json, mode="r", encoding="utf-8")
        db_data = json.load(db)
        db.close()
        if db_data[0]["app"] == name:
            print(f"{name} already exists")
        else:
            db = open(apps_json, mode="w", encoding="utf-8")
            db_data.append(new_app)
            db.write(json.dumps(db_data, indent=2))
    else:
        db = open(apps_json, mode="w", encoding="utf-8")
        final_list = [new_app]
        db.write(json.dumps(final_list, indent=2))
        db.close()


def get_info_from_json(name):

    db = open(apps_json, mode="r")
    db_data = json.load(db)
    db.close()
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

    tarball = requests.get(gh_dl, stream=True)
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

    if remote == "github":
        print("Download source from GitHub...\n")
        dl_gh_source(name, repo, latest_tag)
    elif remote == "gitlab":
        print("Download source from Gitlab...\n")
        clone(name, repo, branch, remote)

    print(f"Building {name}...\n")

    app_working_dir = os.path.join(working_dir, os.listdir(working_dir)[0])

    os.chdir(app_working_dir)
    try:
        subprocess.check_call(shlex.split("./gradlew clean build"))
        apk_loc = copy_build(name, latest_tag)
        if single:
            print(f"Build successful for {name}\n Find APK at {apk_loc}")
    except:
        if single:
            print(f"Build failed for {name}, exiting...\n")


def copy_build(name, latest_tag):
    date = datetime.date.today()
    app_out_dir = os.path.join(out_dir, f"{name}-{latest_tag}-{date}")
    unsigned_apk_name = f"{name}-{latest_tag}-{date}-unsigned.apk"
    dest = os.path.join(app_out_dir, unsigned_apk_name)
    os.mkdir(app_out_dir)
    releaseapk = str(list(pathlib.Path(working_dir).rglob("*release*.apk"))[0])
    shutil.copyfile(releaseapk, dest)
    return dest


def build_all():
    db = open(apps_json, mode="r")
    db_data = json.load(db)
    db.close()

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

        if args.add_app:
            url_parser(args.add_app)

        if bool(args.from_file):
            from_file()

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
