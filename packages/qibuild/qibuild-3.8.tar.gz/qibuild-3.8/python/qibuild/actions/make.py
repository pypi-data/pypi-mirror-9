## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Build a project

"""

from qisys import ui

import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("make options")
    group.add_argument("--rebuild", "-r", action="store_true", default=False)
    group.add_argument("--coverity", action="store_true", default=False,
                       help="Build using cov-build. Ensure you have "
                       "cov-analysis installed on your machine.")

@ui.timer("qibuild make")
def do(args):
    """Main entry point"""

    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    cmake_builder.build(num_jobs=args.num_jobs, rebuild=args.rebuild,
                        coverity=args.coverity)
