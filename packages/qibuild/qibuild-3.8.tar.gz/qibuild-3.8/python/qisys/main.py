## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Entry point for most of qibuild scripts
"""

import sys
import os

import argparse

import qisys.script

def print_version(script_name):
   sys.stdout.write("%s version 3.8\n" % script_name)

def main():
    script_name = sys.argv[0]
    # setuptools on windows creates a foo-script.py
    if os.name == 'nt':
        script_name = script_name.replace("-script", "")
        script_name = script_name.replace(".py", "")
    script_name = os.path.basename(script_name)
    parser = argparse.ArgumentParser()
    package_name = ("%s.actions" % script_name)
    modules = qisys.script.action_modules_from_package(package_name)

    if len(sys.argv) == 2 and sys.argv[1] == '--version':
        print_version(script_name)
        sys.exit(0)

    qisys.script.root_command_main(script_name, parser, modules)

if __name__ == "__main__":
    sys.argv.pop(0)
    main()
