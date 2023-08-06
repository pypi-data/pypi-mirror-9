## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

from qisys import ui
import qisys.command
import qisys.qixml

import qilinguist.project
import qilinguist.qtlinguist

def new_pml_translator(pml_path):
    return PMLTranslator(pml_path)

class PMLTranslator(qilinguist.project.LinguistProject):
    def __init__(self, pml_path):
        self.pml_path = pml_path
        self.path = os.path.dirname(pml_path)
        self.ts_files = translations_files_from_pml(pml_path)
        self.qm_files = list()
        path = os.path.dirname(pml_path)
        name = get_name(pml_path)
        super(PMLTranslator, self).__init__(name, path)

    def update(self):
        raise NotImplementedError()

    def release(self, raises=True):
        all_ok = True
        for ts_file in self.ts_files:
            qm_file = ts_file.replace(".ts", ".qm")
            input = os.path.join(self.path, ts_file)
            output = os.path.join(self.path, qm_file)
            ok, message = qilinguist.qtlinguist.generate_qm_file(input, output)
            if not ok:
                ui.error(message)
                all_ok = False
            cmd = ["lrelease", "-compress", input, "-qm", output]
            qisys.command.call(cmd)
            self.qm_files.append(output)
        if not all_ok and raises:
            raise Exception("`qilinguist release` failed")
        return all_ok

    def install(self, dest):
        translations_dest = os.path.join(dest, "translations")
        qisys.sh.mkdir(translations_dest, recursive=True)
        for qm_file in self.qm_files:
            qisys.sh.install(qm_file, translations_dest)

    def __repr__(self):
        return "<PMLTranslator for %s>" % self.pml_path


def translations_files_from_pml(pml_path):
    res = list()
    tree = qisys.qixml.read(pml_path)
    root = tree.getroot()
    translations_elem = root.find("Translations")
    if translations_elem is None:
        return list()
    translation_elems = translations_elem.findall("Translation")
    for translation_elem in translation_elems:
        res.append(translation_elem.get("src"))
    return res

def get_name(pml_path):
    tree = qisys.qixml.read(pml_path)
    root = tree.getroot()
    return qisys.qixml.parse_required_attr(root, "name", xml_path=pml_path)
