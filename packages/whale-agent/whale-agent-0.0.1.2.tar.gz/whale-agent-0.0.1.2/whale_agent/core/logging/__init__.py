# -*- coding: utf8 -*-

import logging
from logging import Handler

from whale_agent.core.exceptions.check import CheckException
from whale_agent.utils import string_import


class LogManager(object):

    def __init__(self, config):
        self.config = config

        logging.root.handlers = []
        logging.root.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()

        levels = {
            'CRITICAL': logging.CRITICAL,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'FATAL': logging.FATAL,
            'INFO': logging.INFO,
            'WARN': logging.WARN,
            'WARNING': logging.WARNING,
        }
        self.levels = levels

        handlers = []
        for log_handler in self.config.get('log_handlers'):
            handlers.append(string_import(log_handler))

        for handler in handlers:
            current_handler = handler(config=self.config)
            current_handler.setLevel(levels[self.config.get('log_level')])
            root_logger.addHandler(current_handler)

    def config_check(self):
        loggers = self.config.get('log_handlers')
        log_level = self.config.get('log_level')

        if loggers is None:
            raise CheckException('Please set a log_handlers list in the config file.')

        for logger in loggers:
            string_import(logger)(config=self.config).config_check()

        if log_level is None:
            raise CheckException('Please set log_level in the config file.')

        if log_level not in self.levels:
            raise CheckException('Please set a valid log_level in the config file.')


class BaseLogHandler(Handler):

    LOGGING_MAX_BYTES = 5 * 1024 * 1024

    def __init__(self, config, *args, **kwargs):
        self.config = config
        super(BaseLogHandler, self).__init__(*args, **kwargs)

    def get_log_date_format(self):
        return "%Y-%m-%d %H:%M:%S %Z"

    def config_check(self):
        return True
