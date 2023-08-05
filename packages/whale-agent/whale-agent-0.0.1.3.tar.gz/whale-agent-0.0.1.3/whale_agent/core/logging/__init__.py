# -*- coding: utf8 -*-

from abc import abstractmethod
import logging
from logging import Handler

from whale_agent.utils import string_import
from whale_agent.core.exceptions.check import CheckException

log = logging.getLogger(__name__)


class LogManager(object):

    levels = {
        'CRITICAL': logging.CRITICAL,
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'FATAL': logging.FATAL,
        'INFO': logging.INFO,
        'WARN': logging.WARN,
        'WARNING': logging.WARNING,
    }

    def __init__(self, config):
        self.config = config

    def set_up(self):
        log_handlers = self.config.get('log_handlers', [])
        log_level = self.levels[self.config.get('log_level', 'INFO')]

        # Exit logging setup if no loggers exist
        if len(log_handlers) == 0:
            return

        logging.root.handlers = []
        logging.root.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()

        handlers = []
        for log_handler in log_handlers:
            handlers.append(string_import(log_handler))

        for handler in handlers:
            current_handler = handler(config=self.config)
            current_handler.set_up()
            current_handler.setLevel(log_level)
            root_logger.addHandler(current_handler)

    def config_check(self):
        # Check handlers
        log_handlers = self.config.get('log_handlers', [])
        if len(log_handlers) == 0:
            log.warn('No log handlers are set in the config. Using console handler.')
        else:
            for handler in log_handlers:
                try:
                    logger = string_import(handler)
                    current_logger = logger(self.config)
                    current_logger.config_check()
                except ImportError:
                    raise CheckException('Could not import the log handler: %s' % handler)

        # Check log level
        log_level = self.config.get('log_level')
        if log_level is None:
            log.warn('Could not find log level in config. Using INFO level.')
        else:
            if log_level not in self.levels:
                raise CheckException('The log level %s is not valid.' % log_level)


class BaseLogHandler(Handler):

    LOGGING_MAX_BYTES = 5 * 1024 * 1024

    def __init__(self, config, *args, **kwargs):
        self.config = config
        super(BaseLogHandler, self).__init__(*args, **kwargs)

    def get_log_date_format(self):
        return "%Y-%m-%d %H:%M:%S %Z"

    def config_check(self):
        return True

    @abstractmethod
    def set_up(self):
        raise NotImplementedError('Please implement the set_up method.')
