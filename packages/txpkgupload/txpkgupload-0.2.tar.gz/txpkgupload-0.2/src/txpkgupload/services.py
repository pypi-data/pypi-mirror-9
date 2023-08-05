# Copyright 2009-2015 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Additional services that compose txpkgupload."""

from __future__ import (
    print_function,
    unicode_literals,
    )

__metaclass__ = type
__all__ = [
    "PkgUploadFileLogObserver",
    "PkgUploadServices",
    "ReadyService",
    ]

import signal
import sys

import oops
from oops_datedir_repo import DateDirRepo
from oops_twisted import (
    Config as oops_config,
    defer_publisher,
    OOPSObserver,
    )
from twisted.application.service import (
    MultiService,
    Service,
    )
from twisted.internet import reactor
from twisted.python import log
from twisted.python.components import Componentized
from twisted.python.logfile import LogFile
from twisted.python.syslog import SyslogObserver
from twisted.scripts.twistd import ServerOptions


class PkgUploadFileLogObserver(log.FileLogObserver):
    """Like log.FileLogObserver, but honours debug=True in events."""

    def __init__(self, f, debug=False):
        log.FileLogObserver.__init__(self, f)
        self.debug = debug

    def emit(self, eventDict):
        if self.debug or not eventDict.get("debug", False):
            log.FileLogObserver.emit(self, eventDict)


class ReadyService(Service):
    """Service that logs a 'ready!' message once the reactor has started."""

    name = "ready"

    def startService(self):
        reactor.addSystemEventTrigger(
            'after', 'startup', log.msg, 'daemon ready!')
        Service.startService(self)


class PkgUploadServices(MultiService):
    """Container for package upload services."""

    def __init__(self, oops_dir, oops_reporter, server_argv=None):
        MultiService.__init__(self)
        self.oops_dir = oops_dir
        self.oops_reporter = oops_reporter
        self.server_argv = server_argv

    def _getLogObserver(self):
        # We unfortunately have to clone-and-hack part of
        # twisted.scripts._twistd_unix.UnixAppLogger.
        options = ServerOptions()
        options.parseOptions(options=self.server_argv)

        if options.get("syslog", False):
            return SyslogObserver(options.get("prefix", "")).emit

        logfilename = options.get("logfile", "")
        nodaemon = options.get("nodaemon", False)
        if logfilename == "-":
            if not nodaemon:
                sys.exit("Daemons cannot log to stdout, exiting!")
            logFile = sys.stdout
        elif nodaemon and not logfilename:
            logFile = sys.stdout
        else:
            if not logfilename:
                logfilename = "txpkgupload.log"
            logFile = LogFile.fromFullPath(
                logfilename, rotateLength=None, defaultMode=0o644)
            # Override if signal is set to None or SIG_DFL (0)
            if not signal.getsignal(signal.SIGUSR1):
                def reopen_log(signal, frame):
                    reactor.callFromThread(logFile.reopen)
                signal.signal(signal.SIGUSR1, reopen_log)
        log_observer = PkgUploadFileLogObserver(logFile)

        config = oops_config()
        # Add the oops publisher that writes files in the configured place if
        # the command line option was set.
        if self.oops_dir:
            repo = DateDirRepo(self.oops_dir)
            config.publishers.append(
                defer_publisher(oops.publish_new_only(repo.publish)))
        if self.oops_reporter:
            config.template['reporter'] = self.oops_reporter
        oops_observer = OOPSObserver(config, fallback=log_observer.emit)

        return oops_observer.emit

    def setServiceParent(self, parent):
        MultiService.setServiceParent(self, parent)
        if isinstance(parent, Componentized):
            # Customise the application's logging.  We don't get much of an
            # opportunity to do this otherwise.
            parent.setComponent(log.ILogObserver, self._getLogObserver())
