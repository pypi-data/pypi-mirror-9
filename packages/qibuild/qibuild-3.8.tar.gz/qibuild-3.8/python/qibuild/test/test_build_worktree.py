## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import sys

import qibuild.config

from qibuild.test.conftest import TestBuildWorkTree
from qitoolchain.test.conftest import toolchains

import pytest

def test_read_deps(build_worktree):
    build_worktree.create_project("world")
    build_worktree.create_project("hello", build_depends=["world"])
    hello = build_worktree.get_build_project("hello")
    assert hello.build_depends == set(["world"])

def test_setting_build_config_sets_projects_cmake_flags(build_worktree):
    build_worktree.create_project("world")
    build_worktree.build_config.build_type = "Release"
    world = build_worktree.get_build_project("world")
    assert world.cmake_args == ["-DCMAKE_BUILD_TYPE=Release"]

def test_changing_active_config_changes_projects_build_dir(cd_to_tmpdir):
    qibuild.config.add_build_config("foo")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    world_proj = build_worktree.create_project("world")
    assert "foo" in  world_proj.build_directory

def test_project_names_are_unique(build_worktree):
    build_worktree.create_project("foo")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        build_worktree.create_project("foo", src="bar/foo")
    assert "two projects with the same name" in str(e.value)

def test_bad_qibuild2_qiproject(cd_to_tmpdir):
    build_worktree = TestBuildWorkTree()
    build_worktree.create_project("foo")
    foo_qiproj_xml = build_worktree.tmpdir.join("foo").join("qiproject.xml")
    foo_qiproj_xml.write(""" \
<project name="foo">
    <project src="bar" />
</project>
""")
    bar_path = build_worktree.tmpdir.join("foo", "bar").ensure(dir=True)
    bar_path.ensure("CMakeLists.txt").ensure(file=True)
    bar_qiproj_xml = bar_path.join("qiproject.xml")
    bar_qiproj_xml.write("<project />")
    build_worktree = TestBuildWorkTree()

def test_set_default_config(cd_to_tmpdir):
    qibuild.config.add_build_config("foo")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_default_config("foo")
    assert build_worktree.default_config == "foo"
    build_worktree2 = TestBuildWorkTree()
    assert build_worktree2.default_config == "foo"

def test_get_env(toolchains, cd_to_tmpdir):
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    bar_package = toolchains.add_package("foo", "bar")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    world_proj = build_worktree.create_project("world")
    env = build_worktree.get_env()
    if sys.platform.startswith("linux"):
        assert env["LD_LIBRARY_PATH"] == "%s:%s" % (
                os.path.join(world_proj.sdk_directory, "lib"),
                os.path.join(bar_package.path, "lib"))
    if sys.platform.startswith("win"):
        old_path = os.environ["PATH"]
        assert env["PATH"] == "%s;%s;%s" % (
                os.path.join(world_proj.sdk_directory, "bin"),
                os.path.join(bar_package.path, "bin"),
                old_path)
    if sys.platform == "darwin":
        assert env["DYLD_LIBRARY_PATH"] == "%s:%s" % (
                os.path.join(world_proj.sdk_directory, "lib"),
                os.path.join(bar_package.path, "lib"))
        assert env["DYLD_FRAMEWORK_PATH"] == bar_package.path

def test_set_pythonhome(toolchains, cd_to_tmpdir):
    toolchains.create("foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    python_package = toolchains.add_package("foo", "python")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    env = build_worktree.get_env()
    assert env["PYTHONHOME"] == python_package.path

