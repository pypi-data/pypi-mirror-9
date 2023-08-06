## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains functions to manipulate archives.

This module can manipulate:

* ``*.zip`` archives on all platforms
* ``*.tar.gz`` and ``*.tar.bz2`` archives on UNIX
* ``*.tar.xz`` archive is only supported on Linux

The default archive format is zip, to ensure platform interoperability,
and also because this is the qiBuild package format.

All archives should have a unique top directory.

To enforce platform interoperability :

* symlinks are dereferenced:

  * if the source symlink point to a file, the pointed file is archived in place
  * if the source symlink point to a directory, the directory is dropped from
    the archive

* read-only directories are stored with write access

"""

import os
import re
import sys
import posixpath
import operator
import subprocess
import zipfile

import qisys.sh
import qisys.command
from qisys import ui


KNOWN_ALGOS = ["zip", "tar", "gzip", "bzip2", "xz"]

class InvalidArchive(Exception):
    """Just a custom exception """
    def __init__(self, message):
        self._message = message
        Exception.__init__(self)

    def __str__(self):
        return self._message


def _check_algo(algo):
    """ Check that the algo is known

    """
    if algo in KNOWN_ALGOS:
        return
    mess = "Unknown algorithm: %s\n" % algo
    mess += "Known algorithms are: \n"
    for algorithm in KNOWN_ALGOS:
        mess += " * " + algorithm + "\n"
    raise Exception(mess)


def _compress_zip(directory, quiet=True, verbose=False, flat=False, output=None):
    """Compress directory in a .zip file

    :param directory:        directory to add to the archive
    :param archive_basepath: output archive basepath (without extension)
    :param quiet:            quiet mode (print nothing)

    :return: path to the generated archive (archive_basepath.zip)

    """
    if quiet and verbose:
        mess = """Unconsistent arguments: both 'quiet' and 'verbose' options are set.
Please set only one of these two options to 'True'
"""
        raise ValueError(mess)
    ui.debug("Compressing", directory, "to", output)
    archive = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            # Do not zip ourselves
            if full_path == output:
                continue
            rel_path  = os.path.relpath(full_path, directory)
            if flat:
                arcname = rel_path
            else:
                arcname = os.path.join(os.path.basename(directory), rel_path)
            if not quiet:
                sys.stdout.write("adding {0}\n".format(rel_path))
                sys.stdout.flush()
            if not qisys.sh.broken_symlink(full_path):
                archive.write(full_path, arcname)
    archive.close()
    return output


# pylint: disable-msg=R0914
def _extract_zip(archive, directory, quiet, verbose, strict_mode=True):
    """Extract a zip archive into directory

    :param archive:   path of the archive
    :param directory: extract location
    :param quiet:     quiet mode (print nothing)
    :param verbose:   verbose mode (print all the archive content)

    :return: path to the extracted archive (directory/topdir)

    """
    if quiet and verbose:
        mess = """Unconsistent arguments: both 'quiet' and 'verbose' options are set.
Please set only one of these two options to 'True'
"""
        raise ValueError(mess)
    ui.debug("Extracting", archive, "to", directory)
    try:
        archive_ = zipfile.ZipFile(archive)
    except zipfile.BadZipfile:
        mess = 'ZIP file seems corrupted. Try removing it and relaunch command.\n'
        mess += '              rm ' + archive + '\n'
        raise Exception(mess)
    members  = archive_.infolist()
    # There is always the top dir as the first element of the archive
    # (or so we hope)
    ##  BUG ON !!!
    ##    zipped ro files do not appears as members, so the following
    ##    stratement failed if the whole content of the archive is read-only.
    orig_topdir = members[0].filename.split(posixpath.sep)[0]
    size = len(members)
    directories = list()
    for (i, member) in enumerate(members):
        member_top_dir = member.filename.split(posixpath.sep)[0]
        if i != 0 and member_top_dir != orig_topdir:
            # something wrong: members do not have the
            # same basename
            mess  = "Invalid member %s in archive:\n" % member.filename
            mess += "Every file must be in the same top dir (%s != %s)" % \
                (orig_topdir, member_top_dir)
            if strict_mode:
                raise InvalidArchive(mess)
        archive_.extract(member, path=directory)
        # Fix permision on extracted file unless it is a directory
        # or if we are on windows
        if member.filename.endswith("/"):
            directories.append(member)
            new_path = os.path.join(directory, member.filename)
            qisys.sh.mkdir(new_path, recursive=True)
            new_st = 0777
        else:
            new_path = os.path.join(directory, member.filename)
            new_st = member.external_attr >> 16L
        # permissions are meaningless on windows, here only the exension counts
        if not sys.platform.startswith("win"):
            os.chmod(new_path, new_st)

        percent = float(i) / size * 100
        if sys.stdout.isatty():
            message = None
            if not quiet:
                message = "Done: %.0f%%\r" % percent
            elif verbose:
                message = member
            if message:
                sys.stdout.write(message)
                sys.stdout.flush()

    # Reverse sort directories, and then fix perm on these
    directories.sort(key=operator.attrgetter('filename'))
    directories.reverse()

    for zipinfo in directories:
        dirpath = os.path.join(directory, zipinfo.filename)
        new_st = zipinfo.external_attr >> 16L
        if not sys.platform.startswith("win"):
            os.chmod(dirpath, new_st)

    archive_.close()
    ui.debug(archive, "extracted in", directory)
    if strict_mode:
        res = os.path.join(directory, orig_topdir)
    else:
        res = directory
    return res


# pylint: disable-msg=R0913
def _get_tar_command(action, algo, filename, directory, quiet, add_opts=None):
    """Generate a tar command line

    :param action:    compression/exctraction switch [compress|extract]
    :param algo:      compression method
    :param filename:  archive path
    :param directory: directory to add to the archive in case of compression,
                      or extract location in case of extraction
    :param quiet:     quiet mode
    :param add_opts:  list of additional options directly added to the
                      generated tar command line

    :return: the list containing the whole tar commnand

    """
    cmd  = [qisys.command.find_program("tar", raises=True)]
    if not quiet:
        cmd += ["--verbose"]
    if add_opts is not None:
        cmd += add_opts
    if action == "compress":
        cmd += ["--create"]
        cwd  = os.path.dirname(directory)
        data = os.path.basename(directory)
    elif action == "extract":
        cmd += ["--extract"]
        cwd  = directory
        data = None
    if algo != "tar":
        cmd += ["--{0}".format(algo)]
    cmd += ["--file", filename]
    if cwd == "":
        cwd = "."
    cmd += ["--directory", cwd]
    if data is not None:
        cmd += [data]
    return cmd


def _compress_tar(directory, output=None, algo=None,
                  quiet=True, verbose=False):
    """Compress directory in a .tar.* archive

    :param directory:        directory to add to the archive
    :param archive_basepath: output archive basepath (without extension)
    :param algo:             compression method
    :param quiet:            quiet mode (print nothing)
    :param verbose:          verbose mode (print all the archive content)

    :return: path to the generated archive (archive_basepath.tar.*)

    """
    if quiet and verbose:
        mess = """Unconsistent arguments: both 'quiet' and 'verbose' options are set.
Please set only one of these two options to 'True'
"""
        raise ValueError(mess)
    ui.debug("Compressing", directory, "to", output)
    cmd = _get_tar_command("compress", algo, output, directory, quiet)
    try:
        if verbose:
            printed = qisys.command.check_output(cmd, stderr=subprocess.STDOUT)
        else:
            unused_output, printed = qisys.command.check_output_error(cmd)
    except qisys.command.CommandFailedException as err:
        mess  = "Could not compress directory %s\n" % directory
        mess += "(algo: %s)\n" % algo
        mess += "Calling tar failed\n"
        mess += str(err)
        raise Exception(mess)
    return output


def _extract_tar(archive, directory, algo, quiet, verbose, output_filter=None):
    """Extract a .tar.* archive into directory

    :param archive:   path of the archive
    :param directory: extract location
    :param algo:      uncompression method
    :param quiet:     quiet mode (print nothing)
    :param verbose:   verbose mode (print all the archive content)
    :param output_filter:  regex applied on all outputs

    :return: path to the extracted archive (directory/topdir)

    """
    if quiet and verbose:
        mess = """Unconsistent arguments: both 'quiet' and 'verbose' options are set.
Please set only one of these two options to 'True'
"""
        raise ValueError(mess)
    # Because "zip" is the standard qiBuild archive format,
    # do no fancy things but calling "tar", with its default
    # outputs (no progress bar).
    ui.debug("Extracting", archive, "to", directory)
    # first, list the archive and check the topdir of its content
    tar       = qisys.command.find_program("tar")
    list_cmd  = [tar, "--list", "--file", archive]
    process   = subprocess.Popen(list_cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
    line      = process.stdout.readline().split(os.sep, 1)[0]
    topdir    = line.split(os.sep, 1)[0]
    archroot  = None
    opts      = list()
    while len(line) > 0:
        if line[0] in ["/", "."] or topdir != line[0]:
            if process.poll() is None:
                process.terminate()
            if line[0] in ["/", "."]:
                opts.append("--strip-components=1")
                archroot = os.path.basename(archive)
                archroot = archroot.rsplit(".", 1)[0]
                if archroot.endswith(".tar"):
                    archroot = archroot.rsplit(".tar", 1)[0]
            break
        line = process.stdout.readline().split(os.sep, 1)[0]
    if archroot is not None:
        directory = os.path.join(directory, archroot)
        destdir   = directory
    else:
        destdir   = os.path.join(directory, topdir)
    cmd = _get_tar_command("extract", algo, archive, directory, quiet, add_opts=opts)
    qisys.sh.mkdir(directory)
    try:
        if verbose:
            printed = qisys.command.check_output(cmd, stderr=subprocess.STDOUT)
        else:
            unused_output, printed = qisys.command.check_output_error(cmd)
    except qisys.command.CommandFailedException as err:
        mess  = "Could not extract %s to %s\n" % (archive, directory)
        mess += "Calling tar failed\n"
        mess += str(err)
        raise Exception(mess)
    if not quiet:
        for line in str(printed).split("\n"):
            if not output_filter or not re.search(output_filter, line):
                print line.strip()
    return destdir


def compress(directory, algo="zip", output=None, flat=False,
            quiet=False, verbose=False):
    """Compress directory in an archive

    :param directory: directory to add to the archive
    :param archive:   output archive basepath
    :param algo:      compression method (default: zip)
    :param quiet:     silent mode (default: False)
    :param verbose:   verbose mode, print all the archive content
                      (default: False)
    :param flat:      if false, put all files in a common top dir
                      (default: False)

    :return: path to the generated archive

    """
    if quiet and verbose:
        mess = """Unconsistent arguments: both 'quiet' and 'verbose' options are set.
Please set only one of these two options to 'True'
"""
        raise ValueError(mess)
    _check_algo(algo)
    directory = qisys.sh.to_native_path(directory)
    directory = os.path.abspath(directory)
    if output is None:
        output = get_default_output(directory, algo)
    if algo == "zip":
        archive_path = _compress_zip(directory, quiet=quiet, verbose=verbose,
                                     output=output, flat=flat)
    else:
        archive_path = _compress_tar(directory, quiet=quiet, verbose=verbose,
                                     output=output, algo=algo)
    return archive_path

def get_default_output(directory, algo):
    res = directory
    if algo == "tar":
        res += ".tar"
    elif algo == "gzip":
        res += ".tar.gz"
    elif algo == "bzip2":
        res += ".tar.bz2"
    elif algo == "xz":
        res += ".tar.xz"
    elif algo == "zip":
        res += ".zip"
    return res

def extract(archive, directory, algo=None,
                     quiet=False, verbose=False,
                     strict_mode=True):
    """Extract a an archive into directory

    :param archive:   path of the archive
    :param directory: extract location
    :param algo:      uncompression method (default: guessed from the archive name)
    :param quiet:     silent mode (default: False)
    :param verbose:   verbose mode, print all the archive content (default: False)

    :return: path to the extracted archive (directory/topdir)

    """
    if algo:
        _check_algo(algo)
    else:
        algo = guess_algo(archive)
    directory = qisys.sh.to_native_path(directory)
    directory = os.path.abspath(directory)
    archive   = qisys.sh.to_native_path(archive)
    archive   = os.path.abspath(archive)
    if algo == "zip":
        extract_location = _extract_zip(archive, directory, quiet, verbose,
                                        strict_mode=strict_mode)
    else:
        extract_location = _extract_tar(archive, directory, algo, quiet, verbose)
    return extract_location


def guess_algo(archive):
    """Guess the compression algorithm from the archive filename

    :param archive:   path of the archive

    :return: the compression algorithm name

    """
    extension = archive.rsplit(".", 1)[1]
    if "zip" in extension:
        algo = "zip"
    elif "gz" in extension:
        algo = "gzip"
    elif "bz2" in extension:
        algo = "bzip2"
    elif "xz" in extension:
        algo = "xz"
    else:
        algo = extension
    return algo


if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2])
