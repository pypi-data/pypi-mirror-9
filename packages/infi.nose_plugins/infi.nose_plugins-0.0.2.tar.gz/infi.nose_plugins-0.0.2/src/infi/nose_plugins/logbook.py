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

    def begin(self):
        try:
            from logbook.compat import LoggingHandler
            from logbook.concurrency import enable_gevent
        except ImportError:
            pass
        else:
            LoggingHandler().push_application()
            enable_gevent()
