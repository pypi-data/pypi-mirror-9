## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import pytest

import qitest.parsers

def test_nothing_specified_json_in_cwd(args, tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    qitest_json = tmpdir.ensure("qitest.json")
    qitest_json.write("[]")
    test_runner = qitest.parsers.get_test_runner(args)
    assert test_runner.project.sdk_directory == tmpdir.strpath

def test_nothing_specified_inside_qibuild_project(args, build_worktree, monkeypatch):
    world_proj = build_worktree.add_test_project("world")
    world_proj.configure()
    monkeypatch.chdir(world_proj.path)
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.project.sdk_directory == world_proj.sdk_directory

def test_specifying_qitest_json(args, tmpdir):
    qitest_json = tmpdir.ensure("qitest.json")
    qitest_json.write("[]")
    args.qitest_json = qitest_json.strpath
    test_runner = qitest.parsers.get_test_runner(args)
    assert test_runner.project.sdk_directory == tmpdir.strpath

def test_several_qibuild_projects(args, build_worktree, monkeypatch):
    world_proj = build_worktree.add_test_project("world")
    test_proj = build_worktree.add_test_project("testme")
    world_proj.configure()
    test_proj.configure()
    monkeypatch.chdir(build_worktree.root)
    args.projects = ["world", "testme"]
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2
    world_runner, testme_runner = test_runners
    assert world_runner.project.sdk_directory == world_proj.sdk_directory
    assert testme_runner.project.sdk_directory == test_proj.sdk_directory

def test_using_dash_all(args, build_worktree, monkeypatch):
    world_proj = build_worktree.create_project("world")
    hello_proj = build_worktree.create_project("hello")
    world_proj.configure()
    hello_proj.configure()
    args.all = True
    monkeypatch.chdir(build_worktree.root)
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2

def test_several_qitest_json(args, tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    json1 = tmpdir.join("1.json")
    json1.write("[]")
    json2 = tmpdir.join("2.json")
    json2.write("[]")
    args.qitest_jsons = [json1.strpath, json2.strpath]
    qitest.parsers.get_test_runners(args)

def test_qitest_json_from_worktree(args, build_worktree, monkeypatch):
    testme_proj = build_worktree.add_test_project("testme")
    testme_proj.configure()
    monkeypatch.chdir(testme_proj.path)
    qitest_json = os.path.join(testme_proj.sdk_directory, "qitest.json")
    args.qitest_jsons = [qitest_json]
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.cwd == testme_proj.sdk_directory

def test_nothing_to_test(args, cd_to_tmpdir):
    # pylint:disable-msg=E1101
    with pytest.raises(Exception) as e:
        qitest.parsers.get_test_runners(args)
    assert e.value.message == "Nothing found to test"
