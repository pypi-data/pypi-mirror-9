# -*- coding: utf-8 -*-

import logging
import signal
import sys
from datetime import datetime

from .daemon import Daemon, AgentSupervisor
from .config import get_parsed_args, load_config
from .utils import PidFile

from whale_agent.core.logging import LogManager
from whale_agent.core.logging.console import ConsoleHandler
from whale_agent.core.exceptions.check import CheckException
from whale_agent import VERSION, TITLE, GIT, WEBPAGE, EMAIL, LICENSE, AUTHOR

log = logging.getLogger('WhaleAgent')


class Agent(Daemon):

    def __init__(self, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        self.options = kwargs['options']
        self.config = load_config(self.options.config, self.options)
        self.logging = LogManager(self.config)

        self.emitters = []
        self.checks = []
        self.external_checks = []
        self.collector = None
        self.run_forever = True
        self.runtimes = 0
        self.last_execution = None

    def _handle_sigterm(self, signum, frame):
        log.debug('Caught sigterm. Stopping run loop.')
        sys.exit(0)

    def _handle_sigusr1(self, signum, frame):
        self._handle_sigterm(signum, frame)
        self._do_restart()

    def info(self, verbose=None):
        print(self.get_description())
        self.configcheck()

    def configcheck(self):
        log.info('Running configtest')
        try:
            self.logging.config_check()
        except CheckException as ex:
            log.critical(ex.message)
            sys.exit(1)

    def run(self, config=None):
        # Gracefully exit on sigterm.
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        # A SIGUSR1 signals an exit with an autorestart
        signal.signal(signal.SIGUSR1, self._handle_sigusr1)

        # Handle Keyboard Interrupt
        signal.signal(signal.SIGINT, self._handle_sigterm)

        # Agent code stars here..
        log.info('Machine UUID: %s' % self.config.get('uuid'))
        self.configcheck()
        self.load_modules()
        # Setup the collector and run application..

        while self.run_forever:
            # Run collector and get back the result
            # Whait until min_exec time is greater than 30 seconds
            # Only print result the first 20 runs, do it every 10 runs after that

            self.runtimes += 1

        log.info('Exiting. Bye bye.')
        sys.exit(0)

    def _do_restart(self):
        log.info('Running an auto-restart.')
        sys.exit(AgentSupervisor.RESTART_EXIT_STATUS)

    def get_description(self):
        header = ('%s %s' % (TITLE, VERSION)).ljust(50)
        email = 'E-mail:'.ljust(10) + EMAIL
        website = 'Website:'.ljust(10) + WEBPAGE
        github = 'GitHub:'.ljust(10) + GIT
        license = 'License:'.ljust(10) + LICENSE
        copyright = 'Copyright (c) %s %s' % (AUTHOR, datetime.today().date().year)
        return '\n %s \n %s \n %s \n %s \n %s \n %s \n' % (header, email, website, github, license,
                                                           copyright)

    def load_modules(self):
        log.info('Loading modules')

    @classmethod
    def load_base_logger(cls):
        logging.root.handlers = []
        logging.root.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        console_logger = ConsoleHandler({})
        console_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_logger)


def main():

    Agent.load_base_logger()

    options, args = get_parsed_args()

    commands = [
        'start',
        'stop',
        'restart',
        'foreground',
        'status',
        'info',
        'configcheck',
    ]
    start_commands = ['start', 'restart', 'foreground']

    if len(args) < 1:
        sys.stderr.write('Usage: %s %s\n' % (sys.argv[0], '|'.join(commands)))
        return 2

    command = args[0]
    if command not in commands:
        sys.stderr.write('Unknown command: %s\n' % command)
        return 3

    pid_file = PidFile('whale-agent')

    agent = Agent(pid_file.get_path(), options=options)

    if command in start_commands:
        log.info('Agent version %s' % VERSION)

    if 'start' == command:
        log.info('Start daemon')
        agent.start()

    elif 'stop' == command:
        log.info('Stop daemon')
        agent.stop()

    elif 'restart' == command:
        log.info('Restart daemon')
        agent.restart()

    elif 'status' == command:
        agent.status()

    elif 'info' == command:
        return agent.info(verbose=options.verbose)

    elif 'foreground' == command:
        logging.info('Running in foreground')
        agent.run()

    elif 'configcheck' == command or 'configtest' == command:
        agent.configcheck()

    return 0


if __name__ == '__main__':
    """
    try:
        sys.exit(main())
    except StandardError:
        # Try our best to log the error.
        log.exception('Uncaught error running the Agent')
    """
    main()
