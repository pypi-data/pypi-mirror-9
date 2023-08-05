## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Install all the projects to the given dest
"""

import qisys.parsers
import qipkg.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("dest")

def do(args):
    """Main entry point"""
    pml_builder = qipkg.parsers.get_pml_builder(args)
    dest = args.dest
    pml_builder.install(dest)
