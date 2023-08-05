# Copyright 2009-2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

__all__ = [
    'Hooks',
    'InterfaceFailure',
    ]


import os
import time

from twisted.python import log


class InterfaceFailure(Exception):
    pass


class Hooks:

    clients = {}
    LOG_MAGIC = "Post-processing finished"
    _targetcount = 0

    def __init__(self, targetpath, targetstart=0, perms=None, prefix=''):
        self.targetpath = targetpath
        self.perms = perms
        self.prefix = prefix

    @property
    def targetcount(self):
        """A guaranteed unique integer for ensuring unique upload dirs."""
        Hooks._targetcount += 1
        return Hooks._targetcount

    def new_client_hook(self, fsroot, host, port):
        """Prepare a new client record indexed by fsroot..."""
        self.clients[fsroot] = {
            "host": host,
            "port": port
            }
        log.msg("Accepting new session in fsroot: %s" % fsroot, debug=True)
        log.msg("Session from %s:%s" % (host, port), debug=True)

    def client_done_hook(self, fsroot, host, port):
        """A client has completed."""

        if fsroot not in self.clients:
            raise InterfaceFailure("Unable to find fsroot in client set")

        log.msg("Processing session complete in %s" % fsroot, debug=True)

        client = self.clients[fsroot]

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        path = "upload%s-%s-%06d" % (
            self.prefix, timestamp, self.targetcount)
        target_fsroot = os.path.join(self.targetpath, path)

        # Move the session directory to the target directory.
        if os.path.exists(target_fsroot):
            log.msg("Targeted upload already present: %s" % path)
            log.msg("System clock skewed?")
        else:
            try:
                os.rename(fsroot, target_fsroot)
            except (OSError, IOError):
                if not os.path.exists(target_fsroot):
                    raise

        # XXX cprov 20071024: We should replace os.system call by os.chmod
        # and fix the default permission value accordingly in txpkgupload
        if self.perms is not None:
            os.system("chmod %s -R %s" % (self.perms, target_fsroot))

        self.clients.pop(fsroot)
        # This is mainly done so that tests know when the
        # post-processing hook has finished.
        log.msg(self.LOG_MAGIC)
