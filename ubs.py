#! /usr/bin/env python

import logging
import argparse
from create import create_project
from compile import compile_project
from package import package_project
from launch import launch_project

# Setting logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fmt = logging.Formatter(datefmt="%H:%M:%S",
                        fmt='%(asctime)s %(levelname)-8s: %(name)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)


def parse_cmds():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", help="Creates an Android project with given name")
    parser.add_argument("--compile", help="Compiles a specific Android project")
    parser.add_argument("--package", help="Generates an Android application for the given project")
    parser.add_argument("--launch", help="Launches an Android application on an active simulator")
    args = parser.parse_args()

    if args.create:
        create_project(name=args.create)
    elif args.compile:
        compile_project(name=args.compile)
    elif args.package:
        package_project(name=args.package)
    elif args.launch:
        launch_project(name=args.launch)
    else:
        parser.print_help()

if __name__ == '__main__':
    parse_cmds()