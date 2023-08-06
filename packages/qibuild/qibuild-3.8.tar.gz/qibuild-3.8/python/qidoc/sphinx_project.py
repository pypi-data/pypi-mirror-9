## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import sys

from qisys import ui
import qisys.archive
import qisys.sh
import qidoc.project
import pprint


class SphinxProject(qidoc.project.DocProject):
    """ A doc project using Sphinx """
    def __init__(self, doc_worktree, project, name,
                 depends=None, dest=None):
        self.doc_type = "sphinx"
        self.examples = list()
        super(SphinxProject, self).__init__(doc_worktree, project, name,
                                            depends=depends,
                                            dest=dest)
    @property
    def source_dir(self):
        return os.path.join(self.path, "source")


    def configure(self, **kwargs):
        """ Create a correct conf.py in self.build_dir """
        rel_paths = kwargs.get("rel_paths", False)
        in_conf_py = os.path.join(self.source_dir, "conf.in.py")
        should_use_template = False
        if os.path.exists(in_conf_py):
            should_use_template = True
        else:
            in_conf_py = os.path.join(self.source_dir, "conf.py")
            if not os.path.exists(in_conf_py):
                ui.error("Could not find a conf.py or a conf.in.py in", self.source_dir)
                return

        with open(in_conf_py) as fp:
            conf = fp.read()

        if should_use_template:
            if self.template_project:
                from_template = self.template_project.sphinx_conf
                from_template = from_template.format(**kwargs)
                conf = from_template + conf
            else:
                ui.warning("Found a conf.in.py but no template project found "
                           "in the worktree")

        from_conf = dict()
        try:
            # quick hack if conf.in.py used __file__
            from_conf["__file__"] = in_conf_py
            exec(conf, from_conf)
            conf = conf.replace("__file__", 'r"%s"' % in_conf_py)
        except Exception, e:
            ui.error("Could not read", in_conf_py, "\n", e)
            return

        if "project" not in from_conf:
            conf += '\nproject = "%s"\n' % self.name

        if "version" not in from_conf:
            if kwargs.get("version"):
                conf += '\nversion = "%s"\n' % kwargs["version"]


        if should_use_template and self.template_project:
            if "html_theme_path" not in from_conf:
                conf += '\nhtml_theme_path = [r"%s"]\n' % self.template_project.themes_path

        conf += self.append_doxylink_settings(conf, rel_paths=rel_paths)
        conf += self.append_intersphinx_settings(conf, rel_paths=rel_paths)
        conf += self.append_qiapidoc_settings(conf, rel_paths=rel_paths)

        out_conf_py = os.path.join(self.build_dir, "conf.py")
        qisys.sh.write_file_if_different(conf, out_conf_py)


    def append_qiapidoc_settings(self, conf, rel_paths=False):
        """ Return a string representing the qiapidoc settings """
        path_list = []
        self.append_doxy_xml_path(path_list)
        return (
            "\nqiapidoc_srcs=["
            + ','.join(map(lambda x: "r'" + x + "'", path_list))
            + "]\n")

    def append_doxylink_settings(self, conf, rel_paths=False):
        """ Return a string representing the doxylink settings """
        res = self.append_extension(conf, "sphinxcontrib.doxylink")

        doxylink = dict()
        for doxydep in self.doxydeps:
            if rel_paths:
                dep_path = os.path.relpath(doxydep.dest, self.dest)
                dep_path = qisys.sh.to_posix_path(dep_path)
            else:
                dep_path = r"%s"  % doxydep.html_dir
            doxylink[doxydep.name] = (doxydep.tagfile, dep_path)

        res += "\ndoxylink = %s\n" % str(doxylink)
        return res

    def append_intersphinx_settings(self, conf, rel_paths=False):
        """ Return a string representing the intersphinx settings """
        res = self.append_extension(conf, "sphinx.ext.intersphinx")
        sphinx_deps = list()
        for dep_name in self.depends:
            doc_project = self.doc_worktree.get_doc_project(dep_name, raises=False)
            if doc_project and doc_project.doc_type == "sphinx":
                sphinx_deps.append(doc_project)

        intersphinx_mapping = dict()
        for sphinx_dep in sphinx_deps:
            if rel_paths:
                dep_path = os.path.relpath(sphinx_dep.dest, self.dest)
                dep_path = qisys.sh.to_posix_path(dep_path)
            else:
                dep_path = sphinx_dep.html_dir

            intersphinx_mapping[sphinx_dep.name] = (
                dep_path,
                os.path.join(r"%s" % sphinx_dep.html_dir, "objects.inv")
            )

        res += "\nintersphinx_mapping= " + str(intersphinx_mapping)
        return res

    def append_extension(self, conf, extension_name):
        from_conf = dict()
        exec(conf, from_conf)
        res = ""
        if "extensions" not in from_conf:
            res += "extensions = list()\n"
        res += '\nextensions.append("%s")' % extension_name
        return res

    def build(self, **kwargs):
        """ Run sphinx.main() with the correct arguments """
        try:
            import sphinx
        except ImportError, e:
            ui.error(e, "skipping build")
            return

        if self.prebuild_script:
            ui.info(ui.green, "Running pre-build script:",
                    ui.white, self.prebuild_script)
            cmd = [sys.executable, self.prebuild_script]
            qisys.command.call(cmd, cwd=self.path)
            ui.info()

        self.generate_examples_zips()

        html_dir = os.path.join(self.build_dir, "html")
        qisys.sh.mkdir(html_dir, recursive=True)
        spell_dir = os.path.join(self.build_dir, "spellcheck")
        qisys.sh.mkdir(spell_dir, recursive=True)
        if kwargs.get("spellcheck"):
            cmd = [sys.executable, "-c", self.build_dir, "-b", "spelling"]
        else:
            cmd = [sys.executable, "-c", self.build_dir, "-b", "html"]
        if kwargs.get("werror"):
            cmd.append("-W")
        cmd.append(self.source_dir)
        if kwargs.get("spellcheck"):
            cmd.append(spell_dir)
        else:
            cmd.append(html_dir)
        build_type = kwargs.get("build_type")
        if build_type:
            os.environ["build_type"] = build_type
        ui.debug("launching:", cmd)
        try:
            rc = sphinx.main(argv=cmd)
        except SystemExit as e:
            rc = e.code
        if kwargs.get("spellcheck"):
            num_errors = get_num_spellcheck_errors(self.build_dir)
            if num_errors != 0:
                raise SphinxBuildError(self)
        if rc != 0:
            raise SphinxBuildError(self)

    def generate_examples_zips(self):
        for example_src in self.examples:
            example_path = os.path.join(self.source_dir, example_src)
            zip_path = os.path.join(self.source_dir, example_src + ".zip")
            if not qisys.sh.up_to_date(zip_path, example_path):
                ui.info("Generating", zip_path)
                qisys.archive.compress(example_path, algo="zip", quiet=True)

    def install(self, destdir):
        for example_src in self.examples:
            example_path = os.path.join(self.source_dir, example_src)
            real_dest = os.path.join(destdir, example_src)
            qisys.sh.install(example_path, real_dest, quiet=True)

        qisys.sh.install(self.html_dir, destdir)

def get_num_spellcheck_errors(build_dir):
    output_txt = os.path.join(build_dir, "spellcheck", "output.txt")
    res = 0
    if not os.path.exists(output_txt):
        return 1  # so that we raise SphinxBuildError
    with open(output_txt, "r") as fp:
        lines = fp.readlines()
        res = len(lines)
    if res != 0:
        ui.error("Found %i spelling error(s). See %s for the details" %
                 (res, output_txt))
    return res

class SphinxBuildError(Exception):
    def __str__(self):
        return "Error occurred when building doc project: %s" % self.args[0].name
