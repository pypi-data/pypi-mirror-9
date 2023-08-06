from __future__ import with_statement
from fabric.api import run, env, hide
import inspect

def is_enabled(service):
    '''service enabled or not.'''

    func = inspect.stack()[0][3] + '_' + env.get("platform_family", 'rhel')
    return eval(func)(service)

def is_enabled_rhel(service):
    with hide("everything"):
        return "3:on" in run("chkconfig --list %s; true" % service)

def is_enabled_debian(service):
    with hide("everything"):
        return service in run("ls /etc/rc2.d; true")

def is_enabled_freebsd(service):
    with hide("everything"):
		return "YES" in run("cat /etc/rc.conf /usr/local/etc/rc.conf | grep %s_enable; true" % service)

def is_disabled(service):
    '''service disabled or not.'''

    return not is_enabled(service)
