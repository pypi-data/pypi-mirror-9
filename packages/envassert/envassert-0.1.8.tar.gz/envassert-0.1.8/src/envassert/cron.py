from __future__ import with_statement
from fabric.api import run, sudo, hide


def has_entry(user, entry):
	return has_entry_self(entry)

def has_entry_self(entry):
    with hide("everything"):
        return entry in run('crontab -l; true')

def has_entry_sudo(user, entry):
    with hide("everything"):
        return entry in sudo('crontab -u %s -l; true' % user)
