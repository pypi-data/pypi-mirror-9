from nose.plugins import Plugin as NosePlugin
from logging import getLogger
logger = getLogger(__name__)

NOSE_ENV = dict(NOSE_LOGFORMAT="%(asctime)-15s %(levelname)s:%(name)-40s:%(message)s",
                NOSE_LOGFILTER="-infi.storagemodel.errors,-gipc,-passlib")


class LoggingToStderrPlugin(NosePlugin):
    """logging to stderr"""
    name = 'logging-to-stderr'

    def help(self):
        return "logging to stderr"

    def stopContext(self, context):
        pass

    def startContext(self, context):
        import logging
        import sys
        root_logger = logging.getLogger()
        if hasattr(root_logger, "handlers"):
            for handler in root_logger.handlers:
                root_logger.removeHandler(handler)
        kwargs = dict(level=logging.DEBUG, stream=sys.stderr, format=NOSE_ENV['NOSE_LOGFORMAT'])
        logging.basicConfig(**kwargs)

        for handler in root_logger.handlers:
            handler.addFilter(self)

    def filter(self, record):
        modules = [item.strip('-') for item in NOSE_ENV['NOSE_LOGFILTER'].split(',')]
        return 0 if any([module in record.name for module in modules]) else 1

    def startTest(self, test):
        logger.debug("test {} started".format(test))

    def endTest(self, test):
        logger.debug("test {} ended".format(test))
