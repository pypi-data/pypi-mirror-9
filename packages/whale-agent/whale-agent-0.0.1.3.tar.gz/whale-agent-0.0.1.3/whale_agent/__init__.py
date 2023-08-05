TITLE = 'Whale Monitroing - Agent'
AUTHOR = 'Whale Monitoring'
EMAIL = 'contact@whale.io'
WEBPAGE = 'https://whale.io'
DESCRIPTION = 'Agent for Whale Monitoring'
VERSION = '0.0.1.3'
GIT = 'https://github.com/WhaleMonitoring/agent/'
LICENSE = 'MIT'
KEYWORDS = 'Whale Monitoring, Agent, Monitoring, Alerting'

# Just for debugging
import sys
DEBUGGING = 'debugging' in sys.argv
if DEBUGGING:
    from whale_agent.cli import main
    main()
