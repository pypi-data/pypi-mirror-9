from __future__ import with_statement
from fabric.api import run, hide


def is_type(fstype, mountpoint):
    with hide("everything"):
        res = run("df -t %s | awk 'NR>=2{print $NF}'" % (fstype))
        return mountpoint in res.split()
