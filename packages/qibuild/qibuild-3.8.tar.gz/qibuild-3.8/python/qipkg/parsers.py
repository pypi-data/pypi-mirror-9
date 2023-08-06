## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """
import copy

from qisys import ui
import qisys.parsers
import qipkg.builder

import qibuild.parsers
import qipy.parsers
import qilinguist.parsers
import qipkg.metapackage
import qipkg.metabuilder


def pml_parser(parser):
    qisys.parsers.build_parser(parser)
    parser.add_argument("pml_path")

def get_pml_builder(args):
    worktree = qisys.parsers.get_worktree(args, raises=False)
    pml_path = args.pml_path
    if pml_path.endswith(".mpml"):
         res = qipkg.metabuilder.MetaPMLBuilder(pml_path, worktree=worktree)
         configure_meta_builder(res, args)
    else:
         res = qipkg.builder.PMLBuilder(pml_path, worktree=worktree)
         configure_builder(res, args)
    return res

def configure_builder(pml_builder, args):
    build_worktree = pml_builder.build_worktree
    if not build_worktree:
        return
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    build_worktree.build_config = build_config
    python_worktree = pml_builder.python_worktree
    config_name = build_config.build_directory(prefix="py")
    python_worktree.config = config_name

def configure_meta_builder(meta_builder, args):
    for pml_builder in meta_builder.pml_builders:
        configure_builder(pml_builder, args)
