## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.sh
from qisys.qixml import etree
import qibuild.build_config
import qibuild.config
import qitoolchain.toolchain

from qibuild.test.conftest import TestBuildWorkTree

def test_read_profiles(build_worktree):
    build_worktree.configure_build_profile("foo", [("WITH_FOO", "ON")])
    qibuild.config.add_build_config("foo", profiles=["foo"])
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    build_config.set_active_config("foo")
    assert build_config.cmake_args == \
            ["-DCMAKE_BUILD_TYPE=Debug", "-DWITH_FOO=ON"]

def test_users_flags_taken_last(build_worktree):
    build_worktree.configure_build_profile("foo", [("WITH_FOO", "ON")])
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    qibuild.config.add_build_config("foo", profiles=["foo"])
    build_config.set_active_config("foo")
    build_config.user_flags = [("WITH_FOO", "OFF")]
    assert build_config.cmake_args == \
            ["-DCMAKE_BUILD_TYPE=Debug",
             "-DWITH_FOO=ON",
             "-DWITH_FOO=OFF"]

def test_sane_defaults(build_worktree):
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator is None
    assert build_config.build_type == "Debug"
    assert build_config.cmake_args == ["-DCMAKE_BUILD_TYPE=Debug"]

def test_read_qibuild_conf(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write("""
<qibuild>
  <defaults>
    <cmake generator="Ninja" />
  </defaults>
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator == "Ninja"
    assert build_config.cmake_args == \
            ["-GNinja", "-DCMAKE_BUILD_TYPE=Debug"]

def test_build_prefix(build_worktree):
    local_xml = build_worktree.qibuild_xml
    with open(local_xml, "w") as fp:
        fp.write("""
<qibuild>
 <build prefix="mybuild" />
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.build_prefix == "mybuild"

def test_read_default_config(build_worktree):
    qibuild.config.add_build_config("foo")
    build_worktree.set_default_config("foo")
    cmake_build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert cmake_build_config.active_build_config.name == "foo"

def test_read_default_config_in_global_config_file(build_worktree):
    qibuild.config.add_build_config("foo")
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    tree = qisys.qixml.read(qibuild_xml)
    root = tree.getroot()
    worktree_elem = root.find("worktree")
    assert worktree_elem is not None
    defaults_elem = worktree_elem.find("defaults")
    assert defaults_elem is not None
    defaults_elem.set("config", "foo")
    qisys.qixml.write(root, qibuild_xml)


    cmake_build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert cmake_build_config.active_build_config.name == "foo"


def test_use_specific_generator_from_default_config(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write("""
<qibuild>
  <defaults>
    <cmake generator="Ninja" />
  </defaults>
  <config name="vs2010">
    <cmake generator="Visual Studio 2010" />
  </config>
</qibuild>
""")
    qitoolchain.toolchain.Toolchain("vs2010")
    build_worktree.set_default_config("vs2010")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator == "Visual Studio 2010"

def test_set_config_name(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write("""
<qibuild>
  <defaults>
    <cmake generator="Ninja" />
  </defaults>
  <config name="vs2010">
    <cmake generator="Visual Studio 2010" />
  </config>
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    assert build_config.cmake_generator == "Ninja"
    build_config.set_active_config("vs2010")
    assert build_config.cmake_generator == "Visual Studio 2010"

def test_build_env(build_worktree):
    qibuild_xml = qisys.sh.get_config_path("qi", "qibuild.xml")
    with open(qibuild_xml, "w") as fp:
        fp.write(r"""
<qibuild>
  <defaults>
    <env path="c:\swig" />
  </defaults>
  <config name="mingw">
    <env path="c:\mingw\bin" />
  </config>
</qibuild>
""")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    build_config.set_active_config("mingw")
    path = build_config.build_env["PATH"]
    assert r"c:\swig" in path
    assert r"c:\mingw\bin" in path

def test_local_cmake(build_worktree):
    qibuild.config.add_build_config("foo")
    foo_cmake = os.path.join(build_worktree.root, ".qi", "foo.cmake")
    with open(foo_cmake, "w") as fp:
        fp.write("")
    build_config = qibuild.build_config.CMakeBuildConfig(build_worktree)
    build_config.set_active_config("foo")
    assert build_config.local_cmake == foo_cmake

def test_local_and_remote_profiles(build_worktree):
    to_make = os.path.join(build_worktree.dot_qi, "manifests", "default")
    qisys.sh.mkdir(to_make, recursive=True)
    remote_xml = os.path.join(to_make, "manifest.xml")
    with open(remote_xml, "w") as fp:
        fp.write("<qibuild />")
    qibuild.profile.configure_build_profile(remote_xml, "bar", [("WITH_BAR", "ON")])
    local_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(local_xml, "foo", [("WITH_FOO", "ON")])
    build_config = build_worktree.build_config
    qibuild.config.add_build_config("bar", profiles=["bar"])
    qibuild.config.add_build_config("foo", profiles=["foo"])

    build_config.set_active_config("bar")
    assert build_config._profile_flags == [("WITH_BAR", "ON")]

    build_config.set_active_config("foo")
    assert build_config._profile_flags == [("WITH_FOO", "ON")]

def test_overwriting_remote_profiles(build_worktree):
    to_make = os.path.join(build_worktree.dot_qi, "manifests", "default")
    qisys.sh.mkdir(to_make, recursive=True)
    remote_xml = os.path.join(to_make, "manifest.xml")
    with open(remote_xml, "w") as fp:
        fp.write("<qibuild />")
    qibuild.profile.configure_build_profile(remote_xml, "bar", [("WITH_BAR", "ON")])
    local_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(local_xml, "bar", [("WITH_BAR", "OFF")])
    build_config = build_worktree.build_config

    qibuild.config.add_build_config("bar", profiles=["bar"])
    build_config.set_active_config("bar")
    assert build_config._profile_flags == [("WITH_BAR", "OFF")]

def test_profiles_from_config(cd_to_tmpdir):
    qibuild.config.add_build_config("foo", profiles=["bar"])
    build_worktree = TestBuildWorkTree()
    local_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(local_xml, "bar", [("WITH_BAR", "ON")])
    build_worktree.set_active_config("foo")
    build_config = build_worktree.build_config
    assert build_config.profiles == ["bar"]
    assert build_config.cmake_args == ["-DCMAKE_BUILD_TYPE=Debug", "-DWITH_BAR=ON"]
