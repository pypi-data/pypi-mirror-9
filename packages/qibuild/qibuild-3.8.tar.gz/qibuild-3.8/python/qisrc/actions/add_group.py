## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Add a group to the current worktree

"""

from qisys import ui
import qisrc.parsers

import sys

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("group")


def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    group = args.group
    manifest = git_worktree.manifest
    groups = git_worktree.manifest.groups[:]
    if group in groups:
        ui.error("Group", group, "already in use")
        sys.exit(1)
    else:
        groups.append(args.group)
    git_worktree.configure_manifest(manifest.url, groups=groups,
                                    branch=manifest.branch)
