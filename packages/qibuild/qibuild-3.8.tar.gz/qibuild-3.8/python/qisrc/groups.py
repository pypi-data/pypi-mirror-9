## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import xml.etree.ElementTree as etree

import qisys.qixml

from qisys import ui

class Groups(object):
    def __init__(self):
        self.groups = dict()
        self.default_group = None

    def projects(self, group):
        return self.subgroups_group(group)

    def configure_group(self, name, projects, default=False):
        group = Group(name)
        if default:
            group.default = True
        group.projects = projects
        self.groups[name] = group

    def subgroups_group(self, group_name, projects=None):
        if projects is None:
            projects = list()

        group = self.groups.get(group_name)
        if group is None:
            raise GroupError("No such group: %s" % group_name)

        projects.extend(group.projects)

        for subgroup in group.subgroups:
            self.subgroups_group(subgroup, projects=projects)

        return projects

class GroupsParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GroupsParser, self).__init__(target)

    def _parse_group(self, element):
        group_name = element.attrib['name']
        group = Group(group_name)
        parser = GroupParser(group)
        parser.parse(element)
        self.target.groups[group.name] = group
        default = qisys.qixml.parse_bool_attr(element, "default", default=False)
        if default:
            self.target.default_group = group

    def _write_groups(self, element):
        for group in self.target.groups.values():
            parser = GroupParser(group)
            element.append(parser.xml_elem())


class Group(object):
    def __init__(self, name):
        self.name = name
        self.default = False
        self.subgroups = list()
        self.projects = list()

class GroupParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GroupParser, self).__init__(target)

    def _parse_project(self, element):
        self.target.projects.append(element.attrib['name'])

    def _parse_group(self, element):
        self.target.subgroups.append(element.attrib['name'])

    def _write_subgroups(self, element):
        for subgroup in self.target.subgroups:
            parser = GroupParser(subgroup)
            element.append(parser.xml_elem())

    def _write_projects(self, element):
        for project in self.target.projects:
            project_elem = qisys.qixml.etree.Element("project")
            project_elem.set("name", project)
            element.append(project_elem)

def get_root(worktree):
    file = os.path.join(worktree.root, ".qi", "groups.xml")
    if not os.path.exists(file):
        return None
    tree = etree.parse(file)
    return tree.getroot()

def get_groups(worktree):
    root = get_root(worktree)
    if root is None:
        return None
    groups = Groups()
    parser = GroupsParser(groups)
    parser.parse(root)
    return groups

def save_groups(worktree, groups):
    groups_xml_path = os.path.join(worktree.root, ".qi", "groups.xml")
    parser = GroupsParser(groups)
    groups_elem = parser.xml_elem()
    qisys.qixml.write(groups_elem, groups_xml_path)



class GroupError(Exception):
    pass
