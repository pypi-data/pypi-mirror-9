## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains function to handle CMake managed project.

"""

import sys
import os
import re
import subprocess

from qisys import ui
import qisys.command
import qisys.sh
import qibuild.cmake.profiling

def get_known_cmake_generators():
    """ Get the list of known cmake generators.
    Assume cmake is in PATH, or path to cmake is correctly
    configured in ~/.config/qi/qibuild.xml

    """
    build_env = qibuild.config.get_build_env()
    cmake_    = qisys.command.find_program("cmake", env=build_env)
    if not cmake_:
        message = """\
Could not find cmake executable
Please install it if necessary and re-run `qibuild config --wizard`\
"""
        raise Exception(message)
    process = subprocess.Popen([cmake_, "--help"], stdout=subprocess.PIPE)
    (out, _err) = process.communicate()
    intersting  = False
    intersting_lines = list()
    magic_line = "The following generators are available on this platform:"
    # pylint: disable-msg=E1103
    for line in out.splitlines():
        # handle lines like that:
        # Generator = "blalblalba"
        #       files.
        if len(line) >= 3:
            if line[2] == ' ' and not "=" in line:
                continue
        if line == magic_line:
            intersting = True
            continue
        if intersting:
            intersting_lines.append(line)
    to_parse = ""
    for line in intersting_lines:
        to_parse += line.strip()
        # handle lines like that:
        #   Generator
        #           = "blabla"
        if "=" in line:
            to_parse += "\n"
    res = list()
    for line in to_parse.splitlines():
        generator = line.split("=")[0]
        res.append(generator.strip())
    return res

def get_cached_var(build_dir, var, default=None):
    """Get a variable from cmake cache

    :param build_dir: CMakeCache.txt file directory
    :param var:       Requested variable
    :param default:   Default value if not found (default: None)

    :return: the variable value

    """
    cmakecache = os.path.join(build_dir, "CMakeCache.txt")
    if not os.path.exists(cmakecache):
        mess  = "Could not find CMakeCache.txt in %s" % build_dir
        raise Exception(mess)
    res = read_cmake_cache(cmakecache)
    return res.get(var, default)

def cmake(source_dir, build_dir, cmake_args, env=None,
          clean_first=True, profiling=False, debug_trycompile=False,
          trace_cmake=False, summarize_options=False):
    """Call cmake with from a build dir for a source dir.
    cmake_args are added on the command line.

    :param env: defines the environment used when calling ``cmake``
                ``os.environ`` will remain unchanged
    :param clean_first: Clean the cmake cache
    :param summarize_options: Whether to call :py:func:`display_options` at the end

    For qibuild/CMake hackers:

    :param profiling: Profile CMake executions
    :param debug_trycompile: Call ``cmake`` with ``--debug-trycompile``
    :param trace_cmake: Call ``cmake`` with ``--trace`` The results
                        will be written in <build>/cmake.log

    """
    if not os.path.exists(source_dir):
        raise Exception("source dir: %s does not exist, aborting")

    if not os.path.exists(build_dir):
        mess  = "Could not find build directory: %s \n" % build_dir
        raise Exception(mess)

    # Always remove CMakeCache
    if clean_first:
        cache = os.path.join(build_dir, "CMakeCache.txt")
        qisys.sh.rm(cache)

    if debug_trycompile:
        cmake_args.append("--debug-trycompile")
    if profiling or trace_cmake:
        cmake_args.append("--trace")

    # Check that no one has made an in-source build
    in_source_cache = os.path.join(source_dir, "CMakeCache.txt")
    if os.path.exists(in_source_cache):
        # FIXME: better wording
        mess  = "You have run CMake from your sources\n"
        mess += "CMakeCache.txt found here: %s\n" % in_source_cache
        mess += "Please clean your sources and try again\n"
        raise Exception(mess)

    # Check that the root CMakeLists file is correct
    root_cmake = os.path.join(source_dir, "CMakeLists.txt")

    # Add path to source to the list of args, and set buildir for
    # the current working dir.
    cmake_args += [source_dir]
    if not profiling and not trace_cmake:
        qisys.command.call(["cmake"] + cmake_args, cwd=build_dir, env=env)
        if summarize_options:
            display_options(build_dir)
        return
    cmake_log = os.path.join(build_dir, "cmake.log")
    fp = open(cmake_log, "w")
    if profiling:
        ui.info(ui.green, "Running cmake for profiling ...")
    if trace_cmake:
        ui.info(ui.green, "Running cmake with --trace ...")
    ui.debug("Running cmake " + " ".join(cmake_args))
    retcode = subprocess.call(["cmake"] + cmake_args, cwd=build_dir, env=env,
                   stdout=fp, stderr=fp)
    fp.close()
    if retcode != 0:
        mess = "CMake failed"
        if retcode < 0:
            mess += " (%s)" % qisys.command.str_from_signal(-retcode)
        ui.error(mess)
    ui.info(ui.green, "CMake trace saved in", ui.reset, ui.bold, cmake_log)
    if not profiling:
        return
    qibuild_dir = get_cmake_qibuild_dir()
    ui.info(ui.green, "Analyzing cmake logs ...")
    profiling_res = qibuild.cmake.profiling.parse_cmake_log(cmake_log, qibuild_dir)
    outdir = os.path.join(build_dir, "profile")
    qibuild.cmake.profiling.gen_annotations(profiling_res, outdir, qibuild_dir)
    ui.info(ui.green, "Annotations generated in", outdir)

def display_options(build_dir):
    """ Display the options by looking in the CMake cache

    """
    cache_path = os.path.join(build_dir, "CMakeCache.txt")
    print "-- Build options: "
    cache = read_cmake_cache(cache_path)
    opt_keys = [x for x in cache if x.startswith(("WITH_", "ENABLE_"))]
    if not opt_keys:
        print "  <no options found>"
        return
    opt_keys.sort()
    padding = max(len(x) for x in opt_keys) + 3
    for key in opt_keys:
        print "  %s : %s" % (key.ljust(padding), cache[key])

def read_cmake_cache(cache_path):
    """ Read a CMakeCache.txt file, returning a dict
    name -> value

    """
    with open(cache_path, "r") as fp:
        lines = fp.readlines()
    res = dict()
    for line in lines:
        if line.startswith("//"):
            continue
        if line.startswith("#"):
            continue
        if not line:
            continue
        match = re.match(r"([a-zA-Z0-9-_]+):(\w+)=(.*)", line)
        if not match:
            continue
        else:
            (key, _type, value) = match.groups()
            res[key] = value
    return res

def get_cmake_qibuild_dir():
    """Get the path to cmake modules.

    First, look for a project named `qibuild` in the worktree, (if
    a ``worktree`` was passed,
    then, assume we are using qibuild from sources,
    then assume we are using an installed version of qibuild.
    """
    res = find_installed_cmake_qibuild_dir(qibuild.QIBUILD_ROOT_DIR)
    if not res:
        mess  = "Could not find qibuild cmake framework path\n"
        mess += "Please file a bug report with the details of your installation"
        raise Exception(mess)
    return res

def find_installed_cmake_qibuild_dir(python_dir):
    ui.debug("looking for cmake code from", python_dir)
    for candidate in [
        # python in qibuild/python, cmake in qibuild/cmake
        ("..", "..", "cmake"),
        # python in lib/python-2.7/{dist,site}-packages,
        # cmake in share/cmake/
        # (default pip)
        ("..", "..", "..", "..", "share", "cmake"),
        # python in local/lib/python-2.7/{dist,site}-packages,
        # cmake in share/cmake
        # (debian's pip)
        ("..", "..", "..", "..", "..", "share", "cmake"),
        # python in Python27\Lib\{dist,site}-packages
        # cmake in Python27\share\cmake
        # (windows' pip)
        ("..", "..", "..", "share", "cmake"),
        # python in qibuild.egg/qibuild,
        # cmake in qibuild.egg/share/cmake
        # (pip with setuptools)
        ("..", "share", "cmake"),
        # pip on mac
        (sys.prefix, "share", "cmake")
        ]:

        rel_path = os.path.join(*candidate)
        res = os.path.join(python_dir, rel_path)
        res = qisys.sh.to_native_path(res)
        qibuild_config = os.path.join(res, "qibuild", "qibuild-config.cmake")
        ui.debug("trying", qibuild_config)
        if os.path.exists(qibuild_config):
            return res

def get_binutil(name, cmake_var=None, build_dir=None, env=None):
    """ Get a tool from the binutils package.
    First, look for it in the CMake cache, else look for it in the
    system.

    Note that after a call to CMAKE_FORCE_C_COMPILER() in a CMake
    toolchain file, CMAKE_AR, CMAKE_OBJDUMP et al. should be correctly
    set in cache.

    """
    res = None
    if not cmake_var:
        cmake_var = "CMAKE_" + name.upper()
    if build_dir:
        res =  get_cached_var(build_dir, cmake_var)
    if res and not res.endswith("-NOTFOUND"):
        return res
    return qisys.command.find_program(name, env=env)
