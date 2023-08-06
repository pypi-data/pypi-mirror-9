## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qitoolchain.toolchain
from qisrc.test.conftest import svn_server

def get_tc_file_contents(tc):
    """ get the contents of the toolchain file of a toolchain

    """
    tc_file_path = tc.toolchain_file
    with open(tc_file_path, "r") as fp:
        contents = fp.read()
    return contents

def test_get_tc_names():
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain = qitoolchain.toolchain.Toolchain("baz")
    assert qitoolchain.get_tc_names() == ["bar", "baz"]

def test_persistent_storage(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    feed.add_package(boost_package, with_url=True)
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    toolchain2 = qitoolchain.get_toolchain("bar")
    assert toolchain2.packages == toolchain.packages

def test_stores_feed_after_updating(feed):
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    toolchain2 = qitoolchain.toolchain.Toolchain("bar")
    assert toolchain2.feed_url == feed.url

def test_add_local_ctc(tmpdir):
    ctc = tmpdir.mkdir("ctc")
    toolchain_xml = ctc.join("toolchain.xml")
    toolchain_xml.write("""
<toolchain>
  <package name="ctc"
           cross_gdb="cross/bin/i686-linux-gnu-gdb"
           sysroot="sysroot"
           toolchain_file="cross-config.cmake"
           directory="."
  />
  <package name="boost" directory="boost" />
</toolchain>
""")
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(toolchain_xml.strpath)
    tc_contents = get_tc_file_contents(toolchain)
    ctc_path = toolchain.db.get_package_path("ctc")
    config_cmake = os.path.join(ctc_path, "cross-config.cmake")
    assert ('include("%s")' % config_cmake) in tc_contents
    toolchain2 = qitoolchain.toolchain.Toolchain("bar")
    tc_contents = get_tc_file_contents(toolchain2)
    assert ('include("%s")' % config_cmake) in tc_contents


def test_removing(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    feed.add_package(boost_package, with_url=True)
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    toolchain.remove()
    toolchain2 = qitoolchain.toolchain.Toolchain("bar")
    assert not toolchain2.packages

def test_update_svn_package(tmpdir, svn_server):
    boost_url = svn_server.create_repo("boost")
    svn_server.commit_file("boost", "libboost-1.55.so", "")
    feed_xml = """
<toolchain>
  <svn_package name="boost" url="{url}" />
</toolchain>
"""
    feed_xml = feed_xml.format(url=boost_url)
    feed_path = tmpdir.join("feed.xml")
    feed_path.write(feed_xml)
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed_path.strpath)
    boost_package = toolchain.get_package("boost")
    boost_lib = os.path.join(boost_package.path, "libboost-1.55.so")
    assert os.path.exists(boost_lib)

    svn_server.commit_file("boost", "libboost-1.56.so", "")
    toolchain.update()
    boost_lib = os.path.join(boost_package.path, "libboost-1.56.so")
    assert os.path.exists(boost_lib)

def test_sysroot(tmpdir):
    ctc_package = qitoolchain.qipackage.QiPackage("ctc")
    ctc_package.sysroot = "sysroot"
    ctc_package.cross_gdb = "cross-gdb"
    ctc_package.path = tmpdir.strpath
    toolchain = qitoolchain.toolchain.Toolchain("test")
    toolchain.add_package(ctc_package)
    assert toolchain.get_sysroot() == "sysroot"
    assert toolchain.get_cross_gdb() == "cross-gdb"
