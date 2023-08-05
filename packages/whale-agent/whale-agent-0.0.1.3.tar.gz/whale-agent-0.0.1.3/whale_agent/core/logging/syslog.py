# -*- coding: utf8 -*-

import logging
from logging.handlers import SysLogHandler

from whale_agent.core.logging import BaseLogHandler


class SyslogHandler(SysLogHandler, BaseLogHandler):

    def __init__(self, *args, **kwargs):
        BaseLogHandler.__init__(self, *args, **kwargs)

        super(SyslogHandler, self).__init__(facility=SysLogHandler.LOG_DAEMON)

        formatter = logging.Formatter(self.get_syslog_format(),
                                      self.get_log_date_format())
        self.setFormatter(formatter)

    def get_syslog_format(self):
        return '%s[%%(process)d]: %%(name)s(%%(filename)s:%%(lineno)s) %%(levelname)s: ' \
               '%%(message)s' % 'Whale Agent'

    def set_up(self):
        return
