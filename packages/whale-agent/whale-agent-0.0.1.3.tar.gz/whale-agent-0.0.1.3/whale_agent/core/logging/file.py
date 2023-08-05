# -*- coding: utf8 -*-

import logging
from logging.handlers import RotatingFileHandler

from whale_agent.core.exceptions.check import CheckException
from whale_agent.core.logging import BaseLogHandler


class FileHandler(RotatingFileHandler, BaseLogHandler):

    def __init__(self, *args, **kwargs):
        BaseLogHandler.__init__(self, *args, **kwargs)

        log_file = self.config.get('log_file', '/var/log/whale/agent.log')

        super(FileHandler, self).__init__(filename=log_file, maxBytes=self.LOGGING_MAX_BYTES,
                                          backupCount=1)

        formatter = logging.Formatter(self.get_log_format(), self.get_log_date_format())
        self.setFormatter(formatter)

    def get_log_format(self):
        return '%%(asctime)s | %s | %%(name)s(%%(filename)s:%%(lineno)s) | %%(levelname)s' \
               ': %%(message)s' % 'Whale Agent'

    def config_check(self):
        log_file = self.config.get('log_file')

        if not log_file:
            raise CheckException('Please set a log_file parmeter in the config file.')

        super(FileHandler, self).config_check()

    def set_up(self):
        return
