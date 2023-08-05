""" Deploy and install a package to a target

"""

import os
import sys
import zipfile

from qisys import ui

import qisys.command
import qisys.parsers

def configure_parser(parser):
    qisys.parsers.default_parser(parser)
    qisys.parsers.deploy_parser(parser)
    parser.add_argument("pkg_path")

def do(args):
    urls = qisys.parsers.get_deploy_urls(args)
    pkg_path = args.pkg_path
    if pkg_path.endswith(".mpkg"):
        pkg_paths = extract_meta_package(pkg_path)
    else:
        pkg_paths = [pkg_path]
    for url in urls:
        deploy(pkg_paths, url)

def deploy(pkg_paths, url):
    for i, pkg_path in enumerate(pkg_paths):
        ui.info_count(i, len(pkg_paths),
                      ui.green, "Deploying",
                      ui.reset, ui.blue, pkg_path,
                      ui.reset, ui.green, "to",
                      ui.reset, ui.blue, url.as_string)
        scp_cmd = ["scp",
                   pkg_path,
                   "%s@%s:" % (url.user, url.host)]
        qisys.command.call(scp_cmd)

        try:
            _install_package(url, pkg_path)
        except Exception as e:
            ui.error("Unable to install package on target")
            ui.error("Error was: ", e)

def _install_package(url, pkg_path):
    import qi
    session = qi.Session()
    session.connect("tcp://%s:9559" % (url.host))
    package_manager = session.service("PackageManager")
    ret = package_manager.install(
            "/home/%s/%s" % (url.user, os.path.basename(pkg_path)))
    ui.info("PackageManager returned: ", ret)

def extract_meta_package(mpkg_path):
    res = list()
    with zipfile.ZipFile(mpkg_path) as archive:
        members = archive.infolist()
        for (i, member) in enumerate(members):
            if member.filename.endswith("-symbols.zip"):
                continue
            archive.extract(member)
            res.append(member.filename)
    return res
