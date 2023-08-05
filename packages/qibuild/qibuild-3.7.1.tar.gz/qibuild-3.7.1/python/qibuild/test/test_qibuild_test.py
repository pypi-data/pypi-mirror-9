import os
import sys

import xml.etree.ElementTree as etree

import qisys.worktree
import qibuild.worktree

def test_various_outcomes(qibuild_action, record_messages):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("test", "testme", "-k", "ok")
    assert record_messages.find("All pass")
    record_messages.reset()

    rc = qibuild_action("test", "testme", "-k", "fail", retcode=True)
    assert record_messages.find("Return code: 1")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "segfault", retcode=True)
    if os.name == 'nt':
        assert record_messages.find("0xC0000005")
    else:
        assert record_messages.find("Segmentation fault")
    assert rc == 1

    record_messages.reset()
    rc = qibuild_action("test", "testme", "-k", "timeout", retcode=True)
    assert record_messages.find("Timed out")
    assert rc == 1

    rc = qibuild_action("test", "testme", "-k", "spam", retcode=True)
    result_dir = get_result_dir()
    assert "spam.xml" in os.listdir(result_dir)
    result = os.path.join(result_dir, "spam.xml")
    with open(result, "r") as f:
        assert len(f.read()) < 17000

    if qisys.command.find_program("valgrind"):
        # Test one file descriptor leak with --valgrind
        record_messages.reset()
        rc = qibuild_action("test", "testme", "-k", "fdleak","--valgrind", retcode=True)
        assert record_messages.find("file descriptor leaks: 1")
        assert rc == 1

        # Test for false positives with --valgrind
        record_messages.reset()
        rc = qibuild_action("test", "testme", "-k", "ok","--valgrind", retcode=True)
        assert not record_messages.find("file descriptor leaks")
        assert rc == 0

    rc = qibuild_action("test", "testme", "-k", "encoding", retcode=True)
    result_dir = get_result_dir()
    assert "encoding.xml" in os.listdir(result_dir)
    result = os.path.join(result_dir, "encoding.xml")
    with open(result, "r") as f:
        content = f.read()
    # Parsing XML shouldn't raise
    etree.parse(result)
    # Decode shouldn't raise
    if sys.platform.startswith("win"):
        assert "flag" in content.decode("ascii")
    else:
        assert "flag" in content.decode("utf-8")


def get_result_dir():
    worktree = qisys.worktree.WorkTree(os.getcwd())
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    testme = build_worktree.get_build_project("testme")
    result_dir = os.path.join(testme.sdk_directory, "test-results")
    return result_dir

def test_do_not_overwrite_xml_when_test_fails(qibuild_action):
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    qibuild_action("test", "testme", "-k", "fake_gtest", retcode=True)
    testme_proj = qibuild_action.build_worktree.get_build_project("testme")
    fake_xml = os.path.join(testme_proj.sdk_directory, "test-results", "fake_gtest.xml")
    with open(fake_xml, "r") as fp:
        contents = fp.read()
    assert contents == "<gtest>FAKE_RESULTS</gtest>\n"
