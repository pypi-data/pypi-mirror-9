# -*- coding: utf8 -*-

import sys
import logging
from logging.handlers import SysLogHandler

from whale_agent.core.logging import BaseLogHandler


class SyslogHandler(SysLogHandler, BaseLogHandler):

    def __init__(self, *args, **kwargs):
        BaseLogHandler.__init__(self, *args, **kwargs)

        if self.config.get('syslog_host') is not None and \
                self.config.get('syslog_port') is not None:
            sys_log_addr = (self.config.get('syslog_host'), self.config.get('syslog_port'))
        else:
            sys_log_addr = "/dev/log"
            if sys.platform == 'darwin':
                sys_log_addr = "/var/run/syslog"

        super(SyslogHandler, self).__init__(address=sys_log_addr, facility=SysLogHandler.LOG_DAEMON)

        formatter = logging.Formatter(self.get_syslog_format(),
                                      self.get_log_date_format())
        self.setFormatter(formatter)

    def get_syslog_format(self):
        return '%s[%%(process)d]: %%(name)s(%%(filename)s:%%(lineno)s) %%(levelname)s: ' \
               '%%(message)s' % 'Whale Agent'
