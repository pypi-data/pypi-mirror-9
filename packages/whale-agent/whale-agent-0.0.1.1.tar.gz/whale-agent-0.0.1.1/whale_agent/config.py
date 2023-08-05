# -*- coding: utf8 -*-

import logging
import yaml
import sys

from optparse import OptionParser, Values
from yaml.error import YAMLError

from whale_agent.utils import get_uuid

log = logging.getLogger(__name__)


def load_config(config_file=None, options=None):
    default_config_file = '/etc/whale.yaml'

    defaults = {
        'api_endpoint': 'https://whale.io/collector/agent',

        'log_handlers': [
            'whale_agent.core.logging.console.ConsoleHandler',
            'whale_agent.core.logging.syslog.SyslogHandler'
        ],
        'log_level': 'DEBUG'

    }

    if config_file:
        default_config_file = config_file

    log.info('The agent starts reading the config file')
    try:
        with open(default_config_file) as config_file:
            content = config_file.read()
    except IOError:
        log.critical('The agent could not read the config file, the agent will now try to open a '
                     'configfile in the current working directory.')
        try:
            with open('whale.yaml') as config_file:
                content = config_file.read()
        except IOError:
            log.critical('Could not read a config file. The application is exiting.')
            sys.exit(1)

    def yaml_parse_error():
        log.critical('Could not parse config file to a dict. The application is exiting.')
        sys.exit(1)

    config_object = None
    try:
        config_object = yaml.safe_load(content)
    except YAMLError:
        yaml_parse_error()
    if not isinstance(config_object, dict):
        yaml_parse_error()

    result_config = dict(config_object, **defaults)

    log.info('Loading config from arguments')
    if options:
            endpoint = options.whale_url
            if endpoint:
                result_config['api_endpoint'] = endpoint

    result_config['uuid'] = get_uuid()

    return result_config


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
