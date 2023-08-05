# -*- coding: utf8 -*-

import logging
import sys
from logging import StreamHandler

from whale_agent.core.logging import BaseLogHandler


class ConsoleHandler(StreamHandler, BaseLogHandler):

    def __init__(self, *args, **kwargs):
        BaseLogHandler.__init__(self, *args, **kwargs)
        super(ConsoleHandler, self).__init__(stream=sys.stdout)

    def get_log_format(self):
        return '%%(asctime)s | %s | %%(levelname)s' \
               ': %%(message)s' % 'Whale Agent'

    def set_up(self):
        formatter = logging.Formatter(self.get_log_format(), self.get_log_date_format())
        self.setFormatter(formatter)
