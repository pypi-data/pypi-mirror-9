## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import sys
import os

import qisys.command
import qitest.project
import qibuild.config
import qibuild.find

from qisys.test.conftest import skip_on_win
from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction

def test_running_from_install_dir_dep_in_worktree(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "--runtime", "hello", tmpdir.strpath)

    hello = qibuild.find.find_bin([tmpdir.strpath], "hello")
    qisys.command.call([hello])

    assert not tmpdir.join("include").check()

def test_running_from_install_dir_dep_in_toolchain(cd_to_tmpdir):
    # create a foo toolchain containing the world package
    qibuild_action = QiBuildAction()
    qitoolchain_action = QiToolchainAction()
    build_worktree = qibuild_action.build_worktree
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    build_worktree.worktree.remove_project("world", from_disk=True)

    # install and run hello, (checking that the world lib is
    # installed form the package of the toolchain)
    qibuild_action("configure", "-c", "foo", "hello")
    qibuild_action("make", "-c", "foo", "hello")
    prefix = cd_to_tmpdir.mkdir("prefix")
    qibuild_action("install", "-c", "foo", "hello", prefix.strpath)

    hello = qibuild.find.find_bin([prefix.strpath], "hello")
    qisys.command.call([hello])


def test_devel_components_installed_by_default(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "hello", tmpdir.strpath)
    assert tmpdir.join("include").join("world").join("world.h").check()

def test_setting_prefix(qibuild_action, tmpdir):
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")

    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("install", "--prefix=/usr", "--runtime",
                   "hello", tmpdir.strpath)
    hello = qibuild.find.find([tmpdir.join("usr").strpath], "hello")

def test_using_compiled_tool_for_install(qibuild_action, tmpdir):
    qibuild_action.add_test_project("footool")
    qibuild_action.add_test_project("bar")
    qibuild_action("configure", "bar")
    qibuild_action("make", "bar")
    qibuild_action("install", "bar", tmpdir.strpath)

    foo_out = tmpdir.join("share", "foo", "foo.out")
    assert foo_out.check(file=True)

def test_compile_data(qibuild_action, tmpdir):
    qibuild_action.add_test_project("compile_data")
    qibuild_action("configure", "compile_data")
    qibuild_action("make", "compile_data")
    qibuild_action("install", "compile_data", tmpdir.strpath)
    assert tmpdir.join("share", "foo.out").check(file=True)

def test_failing_compiler_makes_install_fail(qibuild_action, tmpdir):
    qibuild_action.add_test_project("compile_data")
    qibuild_action("configure", "compile_data", "-DFAIL_COMPILER=ON")
    qibuild_action("make", "compile_data")
    error = qibuild_action("install", "compile_data", tmpdir.strpath, raises=True)
    assert error

def test_qi_install_cmake(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme")
    qibuild_action("make", "installme")
    qibuild_action("install", "installme", tmpdir.strpath)
    assert tmpdir.join("share", "data_star", "foo.dat").check(file=True)
    assert tmpdir.join("share", "data_star", "bar.dat").check(file=True)
    assert tmpdir.join("share", "recurse", "a_dir/a_file").check(file=True)
    assert tmpdir.join("share", "recurse", "a_dir/b_dir/c_dir/d_file").check(file=True)

def test_fails_early(qibuild_action, tmpdir):
    qibuild_action.add_test_project("installme")
    qibuild_action("configure", "installme", "-DFAIL_EMPTY_GLOB=TRUE", raises=True)
    qibuild_action("configure", "installme", "-DFAIL_NON_EXISTING=TRUE", raises=True)


def test_install_cross_unix_makefiles(qibuild_action, tmpdir):
    install_cross(qibuild_action, tmpdir, cmake_generator="Unix Makefiles")

def test_install_cross_ninja(qibuild_action, tmpdir):
    install_cross(qibuild_action, tmpdir, cmake_generator="Ninja")

@skip_on_win
def install_cross(qibuild_action, tmpdir, cmake_generator="Unix Makefiles"):
    cross_proj = qibuild_action.add_test_project("cross")
    toolchain_file = os.path.join(cross_proj.path, "toolchain.cmake")
    qibuild_action("configure", "cross",
                   "-G", cmake_generator,
                   "-DCMAKE_TOOLCHAIN_FILE=%s" % toolchain_file)
    qibuild_action("make", "cross",)
    qibuild_action("install", "cross",  tmpdir.strpath)

def test_running_tests_after_install(qibuild_action, tmpdir):
    testme = qibuild_action.add_test_project("testme")
    dest = tmpdir.join("dest")
    testme.configure()
    testme.build()
    testme.install(dest.strpath, components=["test"])
    qitest_json = dest.join("qitest.json")
    assert qitest_json.check(file=True)
    test_project = qitest.project.TestProject(qitest_json.strpath)
    test_runner = qibuild.test_runner.ProjectTestRunner(test_project)
    test_runner.patterns = ["ok"]
    test_runner.cwd = dest.strpath
    ok = test_runner.run()
    assert ok


def test_install_returns(qibuild_action, tmpdir):
    installme = qibuild_action.add_test_project("installme")
    dest = tmpdir.join("dest")
    installme.configure()
    installme.build()
    installed = installme.install(dest.strpath, components=["devel", "runtime"])
    assert set(installed) == {'share/data_star/foo.dat',
                              'share/data_star/bar.dat',
                              'include/relative/foo/foo.h',
                              'include/relative/bar/bar.h',
                              'share/recurse/a_dir/b_dir/c_dir/d_file',
                              'share/recurse/a_dir/a_file',
                              'share/sub/bar.dat',
                              'lib/python2.7/site-packages/py/foo.py'}

def test_install_test_libs(qibuild_action, tmpdir):
    installme = qibuild_action.add_test_project("installme")
    dest = tmpdir.join("dest")
    installme.configure()
    installme.build()
    installme.install(dest.strpath, components=["runtime", "test"])

def test_json_merge_tests(qibuild_action, tmpdir):
    qibuild_action.add_test_project("testme")
    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.join("dest")
    qibuild_action("install", "--all", "--with-tests", dest.strpath)
    # tests from both hello and testme should be in the generated
    # json file
    qitest_json = dest.join("qitest.json")
    tests = qitest.conf.parse_tests(qitest_json.strpath)
    test_names = [x["name"] for x in tests]
    assert "zero_test" in test_names
    assert "ok" in test_names

def test_do_not_write_tests_twice(qibuild_action, tmpdir):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.join("dest")
    qitest_json = dest.join("qitest.json")
    qibuild_action("install", "--all", "--with-tests", dest.strpath)
    tests = qitest.conf.parse_tests(qitest_json.strpath)
    first = len(tests)
    qibuild_action("install", "--all", "--with-tests", dest.strpath)
    tests = qitest.conf.parse_tests(qitest_json.strpath)
    second = len(tests)
    assert first == second

def test_do_not_generate_config_module_for_non_installed_targets(qibuild_action, tmpdir):
    qibuild_action.add_test_project("stagenoinstall")
    qibuild_action("configure", "--all")
    qibuild_action("make", "--all")
    dest = tmpdir.mkdir("dest")
    qibuild_action("install", "--all", dest.strpath)
    assert not dest.join("share", "cmake", "foo", "foo-config.cmake").check(file=True)
