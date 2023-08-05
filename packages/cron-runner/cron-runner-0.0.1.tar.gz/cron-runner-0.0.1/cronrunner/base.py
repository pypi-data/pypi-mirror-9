import logging
import logging.handlers
import sys

import registry


class Base(object):
    jobname = None
    logger = None

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._set_logger_options()

    def _set_logger_options(self):
        formatter = logging.Formatter("[%(name)s] %(asctime)s - %(levelname)s: %(message)s")

        try:
            # setting file handler (max 10 files of 1MB)
            h = logging.handlers.RotatingFileHandler(registry.config.get("logfile", "/var/log/cron-runner.log"), "a",
                                                     1 * 1024 * 1024, 10)
        except IOError, e:
            print "Error opening log, %s" % e
            sys.exit(1)

        if registry.debug:
            # setting stream handler
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            h.setLevel(logging.DEBUG)
            self.logger.addHandler(sh)
        else:
            self.logger.setLevel(logging.WARN)
            h.setLevel(logging.WARN)

        h.setFormatter(formatter)
        self.logger.addHandler(h)

    def debug(self, *args):
        for arg in args:
            self.logger.debug("[job: %s] %s" % (self.jobname, arg))
