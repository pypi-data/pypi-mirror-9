# -*- coding: utf8 -*-

import logging
from optparse import OptionParser, Values

log = logging.getLogger(__name__)


def load_config(options=None):
    return {
        'log_handlers': [
            'whale_agent.core.logging.console.ConsoleHandler',
            'whale_agent.core.logging.syslog.SyslogHandler',
            'whale_agent.core.logging.file.FileHandler',
        ],
        'log_file': '/var/log/whale/agent.log'
    }


def get_parsed_args():
    parser = OptionParser()
    parser.add_option('-d', '--whale_url', action='store', default=None,
                      dest='whale_url')
    parser.add_option('-c', '--config', action='store', default=None,
                      dest='config')
    parser.add_option('-v', '--verbose', action='store_true', default=False,
                      dest='verbose',
                      help='Print out stacktraces for errors in checks')

    try:
        options, args = parser.parse_args()
    except SystemExit:
        # Ignore parse errors
        options, args = Values({'whale_url': None, 'verbose': False, 'config': None}), []
    return options, args
