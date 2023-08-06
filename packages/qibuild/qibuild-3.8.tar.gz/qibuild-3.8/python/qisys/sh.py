## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Common filesystem operations """

# Mostly wrappers around somehow strange-behaving
# shutil functions ...

import os
import sys
import contextlib
import time
import errno
import stat
import shutil
import tempfile
import subprocess
import ntpath
import posixpath

from qisys import ui

try:
    from xdg.BaseDirectory import xdg_cache_home, xdg_config_home, xdg_data_home
except ImportError:
    xdg_config_home = os.path.expanduser("~/.config")
    xdg_cache_home = os.path.expanduser("~/.cache")
    xdg_data_home = os.path.expanduser("~/.local/share")

CONFIG_PATH = xdg_config_home
CACHE_PATH = xdg_cache_home
SHARE_PATH = xdg_data_home

def set_home(home):
    global CONFIG_PATH, CACHE_PATH, SHARE_PATH

    CONFIG_PATH = os.path.join(home, "config")
    CACHE_PATH = os.path.join(home, "cache")
    SHARE_PATH = os.path.join(home, "share")

def get_config_path(*args):
    """ Get a config path to read or write some configuration.

    :param args: a list of subfolders. Those will be created
                 when needed

    """
    return get_path(CONFIG_PATH, *args)

def get_cache_path(*args):
    """ Get a config path to read or write some cached data

    :param args: a list of subfolders. Those will be created
                 when needed

    """
    return get_path(CACHE_PATH, *args)

def get_share_path(*args):
    """ Get a config path to read or write some persistent data

    :param args: a list of subfolders. Those will be created
                 when needed

    """
    return get_path(SHARE_PATH, *args)

def get_path(*args):
    """ Helper for get_*_path methods """
    full_path = os.path.join(*args)
    to_make = os.path.dirname(full_path)
    mkdir(to_make, recursive=True)
    full_path = to_native_path(full_path)
    return full_path

def username():
    """ Get the current user name """
    if os.name != 'nt':
        import pwd
        uid = os.getuid()
        pw_info = pwd.getpwuid(uid)
        if pw_info:
            return pw_info.pw_name
    username = os.environ.get("USERNAME")
    if username:
         return username

def mkdir(dest_dir, recursive=False):
    """ Recursive mkdir (do not fail if file exists) """
    try:
        if recursive:
            os.makedirs(dest_dir)
        else:
            os.mkdir(dest_dir)
    except OSError, e:
        if e.errno == 17:
            # Directory already exists -> we don't care
            pass
        else:
            raise


#pylint: disable-msg=C0103
def ln(src, dst, symlink=True):
    """ ln (do not fail if file exists) """
    try:
        if symlink:
            os.symlink(src, dst)
        else:
            raise NotImplementedError
    except OSError, e:
        if e.errno == 17:
            pass
        else:
            raise

def write_file_if_different(data, out_path, mode="w"):
    """ Write the data to out_path if the content is different
    """
    try:
        with open(out_path, "r") as outr:
            out_prev = outr.read()
        if out_prev == data:
            ui.debug("skipping write to %s: same content" % (out_path))
            return
    except:
        pass
    with open(out_path, mode) as out_file:
        out_file.write(data)


def configure_file(in_path, out_path, copy_only=False, *args, **kwargs):
    """Configure a file.
    :param in_path: input file
    :param out_path: output file

    The out_path needs not to exist, missing leading directories will
    be created if necessary.

    If copy_only is True, the contents will be copied "as is".

    If not, we will use the args and kwargs parameter as in::

        in_content.format(*args, **kwargs)

    """
    mkdir(os.path.dirname(os.path.abspath(out_path)), recursive=True)
    with open(in_path, "r") as in_file:
        in_content = in_file.read()
        if copy_only:
            out_content = in_content
        else:
            out_content = in_content.format(*args, **kwargs)
        write_file_if_different(out_content, out_path)


def _copy_link(src, dest, quiet):
    if not os.path.islink(src):
        raise Exception("%s is not a link!" % src)

    target = os.readlink(src)
        #remove existing stuff
    if os.path.lexists(dest):
        rm(dest)
    if sys.stdout.isatty() and not quiet:
        print "-- Installing %s -> %s" % (dest, target)
    to_make = os.path.dirname(dest)
    mkdir(to_make, recursive=True)
    os.symlink(target, dest)


def _handle_dirs(src, dest, root, directories, filter_fun, quiet):
    """ Helper function used by install()

    """
    installed = list()
    rel_root = os.path.relpath(root, src)
    # To avoid filering './' stuff
    if rel_root == ".":
        rel_root = ""
    new_root = os.path.join(dest, rel_root)

    for directory in directories:
        to_filter = os.path.join(rel_root, directory)
        if not filter_fun(to_filter):
            continue
        dsrc = os.path.join(root, directory)
        ddest = os.path.join(new_root, directory)

        if os.path.islink(dsrc):
            _copy_link(dsrc, ddest, quiet)
            installed.append(directory)
        else:
            if os.path.lexists(ddest) and not os.path.isdir(ddest):
                raise Exception("Expecting a directory but found a file: %s" % ddest)
            mkdir(ddest, recursive=True)
    return installed


def _handle_files(src, dest, root, files, filter_fun, quiet):
    """ Helper function used by install()

    """
    installed = list()
    rel_root = os.path.relpath(root, src)
    if rel_root == ".":
        rel_root = ""
    new_root = os.path.join(dest, rel_root)

    for f in files:
        if not filter_fun(os.path.join(rel_root, f)):
            continue
        fsrc = os.path.join(root, f)
        fdest = os.path.join(new_root, f)
        rel_path = os.path.join(rel_root, f)
        if os.path.islink(fsrc):
            mkdir(new_root, recursive=True)
            _copy_link(fsrc, fdest, quiet)
            installed.append(rel_path)
        else:
            if os.path.lexists(fdest) and os.path.isdir(fdest):
                raise Exception("Expecting a file but found a directory: %s" % fdest)
            if not quiet:
                print "-- Installing %s" % fdest
            mkdir(new_root, recursive=True)
            # We do not want to fail if dest exists but is read only
            # (following what `install` does, but not what `cp` does)
            rm(fdest)
            shutil.copy(fsrc, fdest)
            installed.append(rel_path)
    return installed


def install(src, dest, filter_fun=None, quiet=False):
    """Install a directory or a file to a destination.

    If filter_fun is not None, then the file will only be
    installed if filter_fun(relative/path/to/file) returns
    True.

    If ``dest`` does not exist, it will be created first.

    When installing files, if the destination already exists,
    it will be removed first, then overwritten by the new file.

    This function will preserve relative symlinks between directories,
    used for instance in Mac frameworks::

        |__ Versions
            |__ Current  -> 4.0
            |__ 4        -> 4.0
            |__ 4.0

    Return the list of files installed (with relative paths)
    """
    installed = list()
    # FIXME: add a `safe mode` ala install?
    if not os.path.exists(src):
        mess = "Could not install '%s' to '%s'\n" % (src, dest)
        mess += '%s does not exist' % src
        raise Exception(mess)

    src = to_native_path(src, normcase=False)
    dest = to_native_path(dest, normcase=False)
    ui.debug("Installing", src, "->", dest)
    #pylint: disable-msg=E0102
    # (function IS already defined, that's the point!)
    if filter_fun is None:
        def filter_fun(_unused):
            return True

    if os.path.isdir(src):
        if src == dest:
            raise Exception("source and destination are the same directory")
        for (root, dirs, files) in os.walk(src):
            dirs = _handle_dirs (src, dest, root, dirs,  filter_fun, quiet)
            files = _handle_files(src, dest, root, files, filter_fun, quiet)
            installed.extend(files)
    else:
        # Emulate posix `install' behavior:
        # if dest is a dir, install in the directory, else
        # simply copy the file.
        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(src))
        if src == dest:
            raise Exception("source and destination are the same file")
        mkdir(os.path.dirname(dest), recursive=True)
        if sys.stdout.isatty() and not quiet:
            print "-- Installing %s" % dest
        # We do not want to fail if dest exists but is read only
        # (following what `install` does, but not what `cp` does)
        rm(dest)
        shutil.copy(src, dest)
        installed.append(os.path.basename(src))
    return installed


def safe_copy(src, dest):
    """ Copy a source file to a destination but
    do not overwrite dest if it is more recent than src

    Create any missing directories when necessary

    If dest is a directory, src will be copied inside dest.

    """
    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(src))
    if not up_to_date(dest, src):
        shutil.copy(src, dest)

def up_to_date(output_path, input_path):
    """" Return True if output_path exists and is
    more recent than input_path

    """
    if not os.path.exists(output_path):
        return False
    out_mtime = os.stat(output_path).st_mtime
    in_mtime = os.stat(input_path).st_mtime
    return out_mtime > in_mtime


def copy_git_src(src, dest):
    """ Copy a source to a destination but only copy the
    files under version control.
    Assumes that ``src`` is inside a git worktree

    """
    process = subprocess.Popen(["git", "ls-files", "."], cwd=src,
                                stdout=subprocess.PIPE)
    (out, _) = process.communicate()
    for filename in out.splitlines():
        src_file = os.path.join(src, filename)
        dest_file = os.path.join(dest, filename)
        install(src_file, dest_file, quiet=True)


def rm(name):
    """This one can take a file or a directory.
    Contrary to shutil.remove or os.remove, it:

    * won't fail if the directory does not exist
    * won't fail if the directory contains read-only files
    * won't fail if the file does not exist

    Please avoid using shutil.rmtree ...
    """
    if not os.path.lexists(name):
        return
    if os.path.isdir(name) and not os.path.islink(name):
        ui.debug("Removing directory:", name)
        rmtree(name)
    else:
        ui.debug("Removing", name)
        os.remove(name)


# Taken from gclient source code (BSD license)
def rmtree(path):
    """shutil.rmtree() on steroids.

    Recursively removes a directory, even if it's marked read-only.

    shutil.rmtree() doesn't work on Windows if any of the files or directories
    are read-only, which svn repositories and some .svn files are.  We need to
    be able to force the files to be writable (i.e., deletable) as we traverse
    the tree.

    Even with all this, Windows still sometimes fails to delete a file, citing
    a permission error (maybe something to do with antivirus scans or disk
    indexing).  The best suggestion any of the user forums had was to wait a
    bit and try again, so we do that too.  It's hand-waving, but sometimes it
    works. :/

    On POSIX systems, things are a little bit simpler.  The modes of the files
    to be deleted doesn't matter, only the modes of the directories containing
    them are significant.  As the directory tree is traversed, each directory
    has its mode set appropriately before descending into it.  This should
    result in the entire tree being removed, with the possible exception of
    ``path`` itself, because nothing attempts to change the mode of its parent.
    Doing so would be hazardous, as it's not a directory slated for removal.
    In the ordinary case, this is not a problem: for our purposes, the user
    will never lack write permission on ``path``'s parent.
    """
    if not os.path.exists(path):
        return

    if os.path.islink(path) or not os.path.isdir(path):
        raise Exception('Called rmtree(%s) in non-directory' % path)

    if sys.platform == 'win32':
        # Some people don't have the APIs installed. In that case we'll do without.
        win32api = None
        win32con = None
        try:
            # Unable to import 'XX'
            # pylint: disable=F0401
            import win32api, win32con
        except ImportError:
            pass
    else:
        # On POSIX systems, we need the x-bit set on the directory to access it,
        # the r-bit to see its contents, and the w-bit to remove files from it.
        # The actual modes of the files within the directory is irrelevant.
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

    def remove(func, subpath):
        if sys.platform == 'win32':
            os.chmod(subpath, stat.S_IWRITE)
            if win32api and win32con:
                win32api.SetFileAttributes(subpath, win32con.FILE_ATTRIBUTE_NORMAL)
        try:
            func(subpath)
        except OSError, e:
            if e.errno != errno.EACCES or sys.platform != 'win32':
                raise
            # Failed to delete, try again after a 100ms sleep.
            time.sleep(0.1)
            func(subpath)

    for fn in os.listdir(path):
        # If fullpath is a symbolic link that points to a directory, isdir will
        # be True, but we don't want to descend into that as a directory, we just
        # want to remove the link.  Check islink and treat links as ordinary files
        # would be treated regardless of what they reference.
        fullpath = os.path.join(path, fn)
        if os.path.islink(fullpath) or not os.path.isdir(fullpath):
            remove(os.remove, fullpath)
        else:
            # Recurse.
            rmtree(fullpath)

    remove(os.rmdir, path)


def mv(src, dest):
    """Move a file into a directory, but do not crash
    if dest/src exists

    """
    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(src))
    if os.path.exists(dest):
        rm(dest)
    shutil.move(src, dest)


def ls_r(directory):
    """Returns a sorted list of all the files present in a directory,
    relative to this directory.

    For instance, with::

        foo
        |__ eggs
        |    |__ c
        |    |__ d
        |__ empty
        |__ spam
            |__a
            |__b

    ls_r(foo) returns:
    ["eggs/c", "eggs/d", "empty/", "spam/a", "spam/b"]

    """
    res = list()
    for root, dirs, files in os.walk(directory):
        new_root = os.path.relpath(root, directory)
        if new_root == "." and not files:
            continue
        if new_root == "." and files:
            res.extend(files)
            continue
        if not files and not dirs:
            res.append(new_root + os.path.sep)
            continue
        for f in files:
            res.append(os.path.join(new_root, f))
    res.sort()
    return res


def which(program):
    """
    find program in the environment PATH
    :return: path to program if found, None otherwise
    """
    import warnings
    warnings.warn("qisys.sh.which is deprecated, "
     "use qisys.command.find_program instead")
    from qisys.command import find_program
    return find_program(program)


def to_posix_path(path, fix_drive=False):
    """
    Returns a POSIX path from a DOS path
    :param fix_drive: if True, will replace c: by /c/
    (ala mingw)

    """
    res = os.path.expanduser(path)
    res = os.path.abspath(res)
    res = path.replace(ntpath.sep, posixpath.sep)
    if fix_drive:
        (drive, rest) = os.path.splitdrive(res)
        letter = drive[0]
        return "/" + letter + rest
    return res


def to_dos_path(path):
    """Return a DOS path from a "windows with /" path.
    Useful because people sometimes use forward slash in
    environment variable, for instance
    """
    res = path.replace(posixpath.sep, ntpath.sep)
    return res


def to_native_path(path, normcase=True):
    """Return an absolute, native path from a path,
    :param normcase: make sure the path is all lower-case on
    case-insensitive filesystems
    """
    path = os.path.expanduser(path)
    if normcase:
        path = os.path.normcase(path)
    path = os.path.normpath(path)
    path = os.path.abspath(path)
    path = os.path.realpath(path)
    if sys.platform.startswith("win"):
        path = to_dos_path(path)
    return path


def is_path_inside(a, b):
    """ Returns True if a is inside b

    >>> is_path_inside("foo/bar", "foo")
    True
    >>> is_path_inside("gui/bar/libfoo", "lib")
    False
    """
    a = to_native_path(a)
    b = to_native_path(b)
    a_split = a.split(os.path.sep)
    b_split = b.split(os.path.sep)
    if len(a_split) < len(b_split):
        return False
    for (a_part, b_part) in zip(a_split, b_split):
        if a_part != b_part:
            return False
    return True

def is_empty(path):
    """ Check if a path is empty """
    return os.listdir(path) == list()


class TempDir:
    """This is a nice wrapper around tempfile module.

    Usage::

        with TempDir("foo-bar") as temp_dir:
            subdir = os.path.join(temp_dir, "subdir")
            do_foo(subdir)

    This piece of code makes sure that:

    * a temporary directory named temp_dir has been
      created (guaranteed to exist, be empty, and writeable)

    * the directory will be removed when the scope of
      temp_dir has ended unless an exception has occurred
      and DEBUG environment variable is set.

    """
    def __init__(self, name="tmp"):
        self._temp_dir = tempfile.mkdtemp(prefix=name + "-")

    def __enter__(self):
        return self._temp_dir

    def __exit__(self, type, value, tb):
        if os.environ.get("DEBUG"):
            if tb is not None:
                print "=="
                print "Not removing ", self._temp_dir
                print "=="
                return
        rm(self._temp_dir)


@contextlib.contextmanager
def change_cwd(directory):
    """ Change the current working dir """
    if not os.path.exists(directory):
        mess = "Cannot change working dir to '%s'\n" % directory
        mess += "This path does not exist"
        raise Exception(mess)
    previous_cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(previous_cwd)


def is_runtime(filename):
    """ Filter function to only install runtime components of packages

    """
    # FIXME: this looks like a hack.
    # Maybe a user-generated MANIFEST at the root of the package path
    # would be better?

    basename = os.path.basename(filename)
    basedir = filename.split(os.path.sep)[0]
    if filename.startswith("bin"):
        if sys.platform.startswith("win"):
            if filename.endswith(".exe"):
                return True
            if filename.endswith(".dll"):
                return True
            else:
                return False
        else:
            return True
    if filename.startswith("lib"):
        if filename.endswith((".a", ".lib", ".la", ".pc")):
            return False
        return True
    if filename.startswith(os.path.join("share", "cmake")):
        return False
    if filename.startswith(os.path.join("share", "man")):
        return False
    if basedir == "share":
        return True
    if basedir == "include":
        # exception for python:
        if filename.endswith("pyconfig.h"):
            return True
        else:
            return False
    if basedir.endswith(".framework"):
        return True

    # True by default: better have too much stuff than
    # not enough
    return True


def broken_symlink(file_path):
    """ Returns True if the file is a broken symlink

    """
    return os.path.lexists(file_path) and not os.path.exists(file_path)


def is_binary(file_path):
    """ Returns True if the file is binary

    """
    with open(file_path, 'rb') as fp:
        data = fp.read(1024)
        if not data:
            return False
        if b'\0' in data:
            return True
        return False


def is_executable_binary(file_path):
    """ Returns true if the file:
      * is executable
      * is a binary (i.e not a script)
    """
    if not os.path.isfile(file_path):
        return False
    if not os.access(file_path, os.X_OK):
        return False
    return is_binary(file_path)
