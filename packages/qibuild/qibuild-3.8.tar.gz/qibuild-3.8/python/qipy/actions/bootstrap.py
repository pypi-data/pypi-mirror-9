## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Make all python projects available in the current build configuration

"""
import sys
import os

from qisys import ui
import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("requirements", nargs="*")
    parser.set_defaults(requirements=["pip", "virtualenv", "ipython"])

def do(args):
    python_builder = qipy.parsers.get_python_builder(args)
    ok = python_builder.bootstrap(remote_packages=args.requirements)
    if not ok:
        sys.exit(1)
