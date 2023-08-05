import subprocess

from qisys import ui
import qisys.command

class Svn(object):
    def __init__(self, path):
        self.path = path

    def call(self, *args, **kwargs):
        if not "cwd" in kwargs.keys():
            kwargs["cwd"] = self.path
        ui.debug("svn", " ".join(args), "in", kwargs["cwd"])
        if not "quiet" in kwargs.keys():
            kwargs["quiet"] = False
        svn = qisys.command.find_program("svn", raises=True)
        cmd = [svn]
        cmd.extend(args)
        raises = kwargs.get("raises")
        if raises is False:
            del kwargs["raises"]
            del kwargs["quiet"]
            process = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                **kwargs)
            out = process.communicate()[0]
            # Don't want useless blank lines
            out = out.rstrip("\n")
            ui.debug("out:", out)
            return (process.returncode, out)
        else:
            if "raises" in kwargs:
                del kwargs["raises"]
            qisys.command.call(cmd, **kwargs)

    def commit_all(self, message):
        self.call("add", ".", "--force")
        rc, out = self.call("status", raises=False)
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("!"):
                rest = line.split()[1]
                self.call("remove", rest)
        self.call("commit", "--message", message)
