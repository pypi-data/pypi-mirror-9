# -*- coding: utf-8 -*-

import logging
import signal
import sys
import time
from datetime import datetime, timedelta

from whale_agent import AUTHOR, EMAIL, GIT, LICENSE, TITLE, VERSION, WEBPAGE
from whale_agent.collector import Collector
from whale_agent.config import get_parsed_args, load_config
from whale_agent.core.exceptions.check import CheckException
from whale_agent.core.logging import LogManager
from whale_agent.core.logging.console import ConsoleHandler
from whale_agent.daemon import AgentSupervisor, Daemon
from whale_agent.utils import PidFile

log = logging.getLogger('WhaleAgent')


class Agent(Daemon):

    def __init__(self, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        self.options = kwargs['options']
        self.config = load_config(self.options)
        self.logging = LogManager(self.config)

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

    def configcheck(self):
        try:
            # Log check
            self.logging.config_check()

        except CheckException as e:
            log.critical(e.message)
            sys.exit(1)

    def run(self, config=None):
        # Gracefully exit on sigterm.
        signal.signal(signal.SIGTERM, self._handle_sigterm)

        # A SIGUSR1 signals an exit with an autorestart
        signal.signal(signal.SIGUSR1, self._handle_sigusr1)

        # Handle Keyboard Interrupt
        signal.signal(signal.SIGINT, self._handle_sigterm)

        # Run config check
        self.configcheck()

        # Setup logger
        self.logging.set_up()

        # Setup the collector and run application..
        self.collector = Collector(self.config)

        while self.run_forever:

            self.last_execution = datetime.now()

            self.collector.run()
            result = self.collector.result()

            def print_collector_result(result):
                log.info(str(result))

            if self.runtimes <= 10:
                print_collector_result(result)
                if self.runtimes == 10:
                    log.info('The agent will now only print each tenth result')
            elif self.runtimes % 10 == 0:
                print_collector_result(result)

            self.runtimes += 1

            if self.last_execution:
                earliest_run = self.last_execution + timedelta(seconds=30)
                current_time = datetime.now()
                if earliest_run > current_time:
                    sleep_time = earliest_run - current_time
                    time.sleep(sleep_time.seconds)

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
