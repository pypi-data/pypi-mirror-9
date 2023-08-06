## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import sys
import re
import zipfile

from qisys.qixml import etree
import qisys.version
import qibuild.deps

class QiPackage(object):
    """ Binary package for use with qibuild.

    Package names are unique in a given toolchain.
    path is None until the package is added to a database

    """
    def __init__(self, name, version=None, path=None):
        self.name = name
        self.version = version
        self.target = None
        self.host = None
        self.path = path
        self.url = None
        self.directory = None
        self.toolchain_file = None
        self.sysroot = None
        self.cross_gdb = None
        self.build_depends = set()
        self.run_depends = set()
        self.test_depends = set()

    def load_deps(self):
        """ Parse package.xml, set the dependencies """
        package_xml = os.path.join(self.path, "package.xml")
        if os.path.exists(package_xml):
            xml_root = qisys.qixml.read(package_xml)
            qibuild.deps.read_deps_from_xml(self, xml_root)

    def install(self, destdir, components=None, release=True):
        """ Install the given components of the package to the given destination

        Will read

        * ``install_manifest_<component>.txt`` for each component if the file exists
        * ``<component>.mask`` to exclude files matching some regex if the mask exists
        * if none exits, will apply the ``qisys.sh.is_runtime`` filter when
          installing *runtime* component

        """
        if not components:
            return self._install_all(destdir)
        installed_files = list()
        for component in components:
            installed_for_component = self._install_component(component,
                                                              destdir, release=release)
            installed_files.extend(installed_for_component)
        return installed_files

    def _install_all(self, destdir):
        def filter_fun(x):
            return x != "package.xml"
        return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

    def _install_component(self, component, destdir, release=True):
        installed_files = list()
        manifest_name = "install_manifest_%s.txt" % component
        if not release and sys.platform.startswith("win"):
            manifest_name = "install_manifest_%s_debug.txt" % component
        manifest_path = os.path.join(self.path, manifest_name)
        if not os.path.exists(manifest_path):
            mask = self._read_install_mask(component)
            if release:
                mask.extend(self._read_install_mask("release"))
            if not mask and component=="runtime":
                # retro-compat
                def filter_fun(x):
                    return qisys.sh.is_runtime(x) and x != "package.xml"
                return qisys.sh.install(self.path, destdir,
                                        filter_fun=filter_fun)
            else:
                # avoid install masks and package.xml
                mask.append("exclude .*\.mask")
                mask.append("exclude package\.xml")
                return self._install_with_mask(destdir, mask)
        else:
            with open(manifest_path, "r") as fp:
                lines = fp.readlines()
                for line in lines:
                    line = line.strip()
                    src = os.path.join(self.path, line)
                    dest = os.path.join(destdir, line)
                    qisys.sh.install(src, dest)
                    installed_files.append(line)
            return installed_files

    def _read_install_mask(self, mask_name):
        mask_path = os.path.join(self.path, mask_name + ".mask")
        if not os.path.exists(mask_path):
            return list()
        with open(mask_path, "r") as fp:
            mask = fp.readlines()
            mask = [x.strip() for x in mask]
            # remove empty lines and comments:
            mask = [x for x in mask if x != ""]
            mask = [x for x in mask if not x.startswith("#")]
            for line in mask:
                if not line.startswith(("include ", "exclude ")):
                    mess = "Bad mask in %s\n" % mask_path
                    mess += line + "\n"
                    mess += "line should start with 'include' or 'exclude'"
                    raise Exception(mess)
            return mask

    def _install_with_mask(self, destdir, mask):
        def get_match(line, src):
            words = line.split()
            regex = " ".join(words[1:])
            return re.match(regex, src)

        def filter_fun(src):
            src = qisys.sh.to_posix_path(src)
            positive_regexps = [x for x in mask if x.startswith("include")]
            negative_regexps = [x for x in mask if x.startswith("exclude")]
            for line in positive_regexps:
                match = get_match(line, src)
                if match:
                    return True
            for line in negative_regexps:
                match = get_match(line, src)
                if match:
                    return False
            return True

        return qisys.sh.install(self.path, destdir, filter_fun=filter_fun)

    def __repr__(self):
        return "<Package %s %s>" % (self.name, self.version)

    def __str__(self):
        if self.version:
            res = "%s-%s" % (self.name, self.version)
        else:
            res = self.name
        if self.path:
            res += " in %s" % self.path
        return res

    def __cmp__(self, other):
        if self.name == other.name:
            if self.version is None and other.version is not None:
                return -1
            if self.version is not None and other.version is None:
                return 1
            if self.version is None and other.version is None:
                return 0
            return qisys.version.compare(self.version, other.version)
        else:
            return cmp(self.name, other.name)

def from_xml(element):
    name = element.get("name")
    url = element.get("url")
    if element.tag == "svn_package":
        import qitoolchain.svn_package
        res = qitoolchain.svn_package.SvnPackage(name)
        res.revision = element.get("revision")
    else:
        res = QiPackage(name)
    res.url = url
    res.version = element.get("version")
    res.path = element.get("path")
    res.directory = element.get("directory")
    res.toolchain_file = element.get("toolchain_file")
    res.sysroot = element.get("sysroot")
    res.cross_gdb = element.get("cross_gdb")
    res.target = element.get("target")
    res.host = element.get("host")
    qibuild.deps.read_deps_from_xml(res, element)
    return res

def from_archive(archive_path):
    archive = zipfile.ZipFile(archive_path)
    xml_data = archive.read("package.xml")
    element = etree.fromstring(xml_data)
    return from_xml(element)

def extract(archive_path, dest):
    if archive_path.endswith((".tar.gz", ".tbz2")):
       return _extract_legacy(archive_path, dest)
    with zipfile.ZipFile(archive_path) as archive:
        if "package.xml" in archive.namelist():
            return _extract_modern(archive_path, dest)
        else:
            return _extract_legacy(archive_path, dest)

def _extract_modern(archive_path, dest):
    return qisys.archive.extract(archive_path, dest, strict_mode=False)

def _extract_legacy(archive_path, dest):
    algo = qisys.archive.guess_algo(archive_path)
    extract_dest = os.path.dirname(dest)
    extract_path = qisys.archive.extract(archive_path, extract_dest, algo=algo)
    extract_path = os.path.abspath(extract_path)
    if extract_path != dest:
        qisys.sh.mkdir(dest, recursive=True)
        qisys.sh.rm(dest)
        qisys.sh.mv(extract_path, dest)
        qisys.sh.rm(extract_path)
        return dest
    else:
        return extract_path
