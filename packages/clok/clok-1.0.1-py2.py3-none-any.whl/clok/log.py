#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from logging import handlers


class Logger(object):
    DEFAULT_FORMAT = "[%(asctime)s] [%(name)s] %(levelname)-8s | %(message)s"
    DEFAULT_SYSLOG_ADDRESS = '/dev/log'

    def __init__(self, name='clok'):
        self.logger = logging.getLogger(name)

    def setup(self, level='info', format=None, type='stderr', filename=None):
        """ By default, will log on stderr from lvl DEBUG """
        level = getattr(logging, level.upper())
        if format is None:
            format = Logger.DEFAULT_FORMAT
        if type == 'file':
            handler = logging.FileHandler(filename)
        elif type == 'stderr':
            handler = logging.StreamHandler()
        elif type == 'syslog':
            handler = handlers.SysLogHandler(address=Logger.DEFAULT_SYSLOG_ADDRESS)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(format))
        self.logger.setLevel(level)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def debug(self, *args, **kwargs): return self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs): return self.logger.info(*args, **kwargs)

    def warn(self, *args, **kwargs): return self.logger.warn(*args, **kwargs)

    def warning(self, *args, **kwargs): return self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs): return self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs): return self.logger.critical(*args, **kwargs)
