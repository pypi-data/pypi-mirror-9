## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Open the current documentation in a web browser."""

import os
import sys

from qisys import ui
import qisys.command
import qisys.parsers
import qisys.sh
import qidoc.parsers

import webbrowser

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("-b", "--browser")

def do(args):
    doc_worktree = qidoc.parsers.get_doc_worktree(args)
    doc_project = qidoc.parsers.get_one_doc_project(doc_worktree, args)
    index_html = doc_project.index_html
    if not os.path.exists(doc_project.index_html):
        mess = """ \
The doc project in {path} does no appear to have been built yet.
({index_html} does not exist.
Try running  `qidoc build`
"""
        mess = mess.format(path=doc_project.path, index_html=index_html)
        ui.error(mess)
        sys.exit(1)
    if sys.platform == "darwin":
        index_html = "file://" + index_html
    if args.browser:
        cmd = [args.browser, index_html]
        qisys.command.call(cmd)
    else:
        webbrowser.open(index_html)
