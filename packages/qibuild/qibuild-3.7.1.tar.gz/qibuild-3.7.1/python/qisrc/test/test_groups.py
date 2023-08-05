import xml.etree.ElementTree as etree

import qisrc.groups

import pytest

def test_parser_read():
    file = """
<groups>
  <group name="a">
    <project name="b" />
    <project name="c" />
    <group name="d" />
  </group>
  <group name="d">
    <project name="foo" />
    <project name="bar" />
  </group>
</groups>
"""

    root = etree.fromstring(file)

    groups = qisrc.groups.Groups()
    parser = qisrc.groups.GroupsParser(groups)
    parser.parse(root)

    assert set(groups.projects('d')) - set(['bar', 'foo']) == set()
    assert set(groups.projects('a')) - set(['bar', 'foo', 'b', 'c', 'd']) == set()

    # pylint: disable-msg=E1101
    with pytest.raises(qisrc.groups.GroupError):
        groups.projects("c")

def test_parser_write():
    groups = qisrc.groups.Groups()
    groups.configure_group("mygroup", ["a", "b"])

    parser = qisrc.groups.GroupsParser(groups)
    root = parser.xml_elem()
    groups = qisrc.groups.Groups()
    parser = qisrc.groups.GroupsParser(groups)
    parser.parse(root)
    assert groups.projects("mygroup") == ["a", "b"]

def test_save_groups(worktree):
    groups = qisrc.groups.Groups()
    groups.configure_group("mygroup", ["a", "b"])
    qisrc.groups.save_groups(worktree, groups)
    groups = qisrc.groups.get_groups(worktree)
    assert groups.projects("mygroup") == ["a", "b"]
