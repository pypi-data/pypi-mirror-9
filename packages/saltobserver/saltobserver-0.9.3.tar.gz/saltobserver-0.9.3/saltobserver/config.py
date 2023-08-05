import os

DEBUG = False

LOG_FILE = os.getenv('LOG_FILE', 'saltobserver_app.log')

# If set to false, flask's url handling will be used for external libraries.
# The static directory contains a script to download all dependencies.
USE_CDN = bool(int(os.getenv('SALTOBSERVER_USE_CDN', 1)))
# If set to false, no liveupdates, no websockets
USE_LIVEUPDATES = True

# the function list shown in the webinterface's navbar.
FUNCTION_QUICKLIST = ['state.highstate', 'state.sls', 'pkg.upgrade', 'test.ping']
# the default redirect when visiting /
DEFAULT_FUNCTION = 'state.highstate'

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASS = None
