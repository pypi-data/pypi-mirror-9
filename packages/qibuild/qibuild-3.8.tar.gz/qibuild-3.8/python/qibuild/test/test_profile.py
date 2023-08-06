## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


import qibuild.config
import qibuild.profile

from qisrc.test.conftest import qisrc_action, git_server
from qibuild.test.conftest import TestBuildWorkTree

def test_read_build_profiles(tmpdir):
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("""
<qibuild version="1">
  <profiles>
    <profile name="foo">
      <cmake>
        <flags>
          <flag name="WITH_FOO">ON</flag>
        </flags>
      </cmake>
    </profile>
    <profile name="bar">
      <cmake>
        <flags>
          <flag name="WITH_BAR">ON</flag>
        </flags>
      </cmake>
    </profile>
  </profiles>
</qibuild>
""")
    profiles = qibuild.profile.parse_profiles(qibuild_xml.strpath)
    assert len(profiles) == 2
    assert profiles['foo'].cmake_flags == [("WITH_FOO", "ON")]
    assert profiles['bar'].cmake_flags == [("WITH_BAR", "ON")]

def test_profiles_are_persistent(tmpdir):
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("<qibuild />")
    qibuild.profile.configure_build_profile(qibuild_xml.strpath, "foo", [("WITH_FOO", "ON")])
    assert qibuild.profile.parse_profiles(qibuild_xml.strpath)["foo"].cmake_flags == \
            [("WITH_FOO", "ON")]
    qibuild.profile.remove_build_profile(qibuild_xml.strpath, "foo")
    assert "foo" not in qibuild.profile.parse_profiles(qibuild_xml.strpath)

def test_using_custom_profile(qibuild_action, qisrc_action, git_server):
    git_server.add_build_profile("foo", [("WITH_FOO", "ON")])
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml, "bar", [("WITH_BAR", "ON")])
    build_worktree.create_project("spam")
    qibuild.config.add_build_config("foo", profiles=["foo"])
    qibuild.config.add_build_config("bar", profiles=["bar"])
    qibuild_action("configure", "spam", "--config", "foo", "--summarize-options")
    qibuild_action("configure", "spam", "--config", "bar", "--summarize-options")
