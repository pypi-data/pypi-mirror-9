import qisys.sh
import qisys.script

from qisys.test.conftest import TestWorkTree

def test_qisrc_remove_exsiting(qisrc_action):
    worktree = qisrc_action.worktree
    worktree.create_project("foo")
    qisrc_action("remove", "foo")
    worktree = TestWorkTree()
    assert not worktree.get_project("foo")
    assert worktree.tmpdir.join("foo").check(dir=True)

def test_qisrc_remove_existing_from_disk(qisrc_action):
    worktree = qisrc_action.worktree
    worktree.create_project("foo")
    qisrc_action("remove", "foo", "--from-disk")
    worktree = TestWorkTree()
    assert not worktree.get_project("foo")
    assert not worktree.tmpdir.join("foo").check(dir=True)

def test_qisrc_fails_when_not_exists(qisrc_action):
    error = qisrc_action("remove", "foo", raises=True)
    assert "No such project: foo" in error
