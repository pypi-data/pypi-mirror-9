## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

from qisys import ui
import qisys.sort


class DocBuilder(object):
    """ Build and install doc projects.

    Initialize with a `base_project`, which will
    be at the root of the dest dir when installed.

    The `install` step is required to have redistributable
    documentation folder, while you can browse the documentation
    directly from the build dir.

    """
    def __init__(self, doc_worktree, base_project_name=None):
        self.doc_worktree = doc_worktree
        self.single = False
        self.deps_solver = None
        self.version = "latest"
        self.hosted = True
        self.build_type = ""
        self.werror = False
        self.warnings = True
        self.spellcheck = False
        self._base_project = None
        if base_project_name:
            self.set_base_project(base_project_name)

    @property
    def base_project(self):
        return self._base_project

    def set_base_project(self, name):
        self._base_project = self.doc_worktree.get_doc_project(name, raises=True)
        self._base_project.is_base_project = True

    def configure(self):
        """ Configure the projects in the right order

        """
        projects = self.get_dep_projects()
        configure_args = {
            "version" : self.version,
            "hosted"  : self.hosted,
            "build_type"   : self.build_type,
            "warnings"     : self.warnings
        }
        for project in projects:
            project.configure(**configure_args)

    def build(self):
        """ Build the projects in the right order,
        making sure they are configured first

        """
        projects = self.get_dep_projects()
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Building", ui.blue, project.name)
            project.build(werror=self.werror, build_type=self.build_type,
                          spellcheck=self.spellcheck)
            if not self.spellcheck:
                ui.info(ui.green, "Doc generated in",
                        ui.reset, ui.bold, project.html_dir)

    def install(self, destdir):
        """ Install the doc projects to a dest dir

        """
        projects = self.get_dep_projects()
        for i, project in enumerate(projects):
            real_dest = os.path.join(destdir, project.dest)
            ui.info_count(i, len(projects),
                          ui.green, "Installing",
                          ui.blue, project.name,
                          ui.reset, "->", ui.white, real_dest)
            options = {
                "version"   : self.version,
                "hosted"    : self.hosted,
                "build_type" : self.build_type,
                "rel_paths" : True,
            }
            project.configure(**options)
            project.build(**options)
            project.install(real_dest)

    def get_dep_projects(self):
        """ Get the list of project deps

        """
        if self.single:
            return [self.base_project]
        projects = list()
        dep_tree = dict()
        for project in self.doc_worktree.doc_projects:
            dep_tree[project.name] = project.depends
        base_name = self.base_project.name
        sorted_names = qisys.sort.topological_sort(dep_tree, [base_name])
        for name in sorted_names:
            project = self.doc_worktree.get_doc_project(name, raises=False)
            if project:
                projects.append(project)
        return projects
