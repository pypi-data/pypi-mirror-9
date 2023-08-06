from __future__ import absolute_import
from nose.plugins import Plugin


class LogbookPlugin(Plugin):  # pragma: no cover
    """logbook compatability"""
    name = 'logbook'
    enabled = True

    def configure(self, options, conf):
        super(LogbookPlugin, self).configure(options, conf)
        self.enabled = True

    def help(self):
        return 'logbook compatability'

    def _send_logbook_records_to_standard_logging(self):
        try:
            from logbook.compat import LoggingHandler
        except ImportError:
            pass
        else:
            LoggingHandler().push_application()

    def _enable_logbook_gevent(self):
        try:
            from logbook.concurrency import enable_gevent
        except ImportError:
            pass
        else:
            enable_gevent()

    def begin(self):
        self._enable_logbook_gevent()
        self._send_logbook_records_to_standard_logging()

