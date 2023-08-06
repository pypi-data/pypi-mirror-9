from __future__ import with_statement
from fabric.api import run, hide


def is_listening(port, protocol=None):
    flags = "tunl"
    if protocol == "udp":
        flags = "unl"
    elif protocol == "tcp":
        flags = "tnl"

    with hide("everything"):
        listening = run("netstat -%s | grep -v grep | grep ':%s ' ; true" %
                        (flags, port))
    if listening:
        return True
    else:
        return None
