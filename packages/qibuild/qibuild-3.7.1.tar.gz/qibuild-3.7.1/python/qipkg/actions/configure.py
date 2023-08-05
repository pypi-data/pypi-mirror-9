## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Configure all the projects of the given pml file
"""

import qibuild.parsers
import qipkg.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    qibuild.parsers.cmake_configure_parser(parser)


def do(args):
    """Main entry point"""
    args.cmake_args = qibuild.parsers.get_cmake_args(args)
    pml_builder = qipkg.parsers.get_pml_builder(args)
    pml_builder.configure()

