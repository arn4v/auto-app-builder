#!/usr/bin/env python3
# Copyright (C) 2020 Arnav Gosain
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import bs4
import datetime
import json
import os
import shutil
import subprocess
import sys
import wget
from pathlib import Path

root_dir = os.getcwd()
working_dir = f'{root_dir}/working'
bin_dir = f'{root_dir}/bin'
db = f'{root_dir}/apps.json'
apps = []


def parse_arguments():
    """
    Arguments to be passed into the script
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-b",
                        "--build",
                        metavar="",
                        help="Builds specified app",
                        type=str)
    parser.add_argument(
        "-ba",
        "--build-all",
        metavar="",
        type=bool,
        action="store_true",a   
        default=False,
        help="Builds all app specified in json",
    )
    parser.add_argument(
        "--fdroid",
        metavar="",
        action="store_true",
        default=False,
        help=
        "Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument("-f",
                        "--file",
                        metavar="",
                        nargs=1,
                        help="Read app-list from plain-text file.")
    parser.add_argument(
        "-a",
        "--add-app",
        type=str,
        nargs=2,
        metavar="",
        help=
        "Takes application specifics input form user and stores in a JSON file",
    )
    parser.add_argument(
        "--add-from-file",
        type="str",
        metavar="",
        help=
        "Takes application names from text file, finds specifics from F-Droid and stores it in a new or prexisting JSON file.",
    )
    return parser.parse_args()


def setup_dirs():
    """
    Check if working directory exists and create it if it doesn't
    """
    if os.path.isdir(working_dir) is False:
        os.mkdir(working_dir)

    if os.path.isdir(bin_dir) is False:
        os.mkdir(bin_dir)


# def check_deps():
#     """
#     Check for OS packages: aria2c, curl, java and gradle
#     """
#     if not os.path.isfile(f'{bin_dir}/chrome')


def info_from_fdroid(name):
    get_from_fdroid = False
    fdroid_argv = str(sys.argv[1]).lower
    valid_args = ["fdroid", "f-droid"]

    if fdroid_argv in valid_args:
        return get_from_fdroid


# def parse_to_json(name, branch, repo):
#     if not os.path.isfile('root_dir/apps.json'):
#         with open(os.path.join(path, db), 'w') as appdb:
#             pass


def info_from_user():
    print('Please enter app specifics: \n')
    name = input('Enter app name: \n')
    branch = input('Enter branch to use: \n')
    repo = input('Enter git URL \n')
    # return parse_to_json(name, branch, repo)


def get_info_from_json():
    pass


def fetch_tag_info():
    repository_name = ''
    gh_base_url = f"https://api.github.com/repos/{repository_name}/releases/latest"
    tag_info = requests.get(gh_base_url)


def build():
    pass


def build_all():
    for app in get_all():
        build(app)


def main():

    args = parse_arguments()

    if len(args.add_app) != 0:
        if args.fdroid == True:
            info_from_fdroid(args.add_app)
        else:
            info_from_user()


if __name__ == '__main__':
    main()
