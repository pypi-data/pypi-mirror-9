# Copyright 2009-2015 Canonical Ltd.  This software is licensed under the
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Logging for the SSH server."""

__metaclass__ = type
__all__ = [
    'LoggingManager',
    ]

import logging
from logging.handlers import WatchedFileHandler

from zope.component import (
    adapter,
    getGlobalSiteManager,
    provideHandler,
    )
# This non-standard import is necessary to hook up the event system.
import zope.component.event

from lazr.sshserver.events import ILoggingEvent


class LoggingManager:
    """Class for managing SSH server logging."""

    def __init__(self, main_log, access_log, access_log_path):
        """Construct the logging manager.

        :param main_log: The main log. Twisted will log to this.
        :param access_log: The access log object.
        :param access_log_path: The path to the file where access log
            messages go.
        """
        self._main_log = main_log
        self._access_log = access_log
        self._access_log_path = access_log_path
        self._is_set_up = False

    def setUp(self):
        """Set up logging for the smart server.

        This sets up a debugging handler on the main logger and makes sure
        that things logged there won't go to stderr. It also sets up an access
        logger.
        """
        log = self._main_log
        self._orig_level = log.level
        self._orig_handlers = list(log.handlers)
        log.setLevel(logging.INFO)
        self._main_handler = logging.NullHandler()
        log.addHandler(self._main_handler)
        self._access_handler = WatchedFileHandler(self._access_log_path)
        self._access_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        self._access_log.addHandler(self._access_handler)
        self._access_log.setLevel(logging.INFO)
        # Make sure that our logging event handler is there, ready to receive
        # logging events.
        provideHandler(self._log_event)
        self._is_set_up = True

    @adapter(ILoggingEvent)
    def _log_event(self, event):
        """Log 'event' to the access log."""
        self._access_log.log(event.level, event.message)

    def tearDown(self):
        if not self._is_set_up:
            return
        log = self._main_log
        log.level = self._orig_level
        log.removeHandler(self._main_handler)
        self._access_log.removeHandler(self._access_handler)
        getGlobalSiteManager().unregisterHandler(self._log_event)
        self._is_set_up = False
