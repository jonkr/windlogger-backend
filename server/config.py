import os
import json

def relative(path):
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(
            __file__)), path))

def read_credentials():
    return json.load(open(relative('./../credentials.json')))

CREDENTIALS = read_credentials()

DB_PASSWORD = CREDENTIALS['postgresPassword']
DB_USER = 'windlogger'
DB_NAME = 'windlogger'
DB_URI = 'postgresql+psycopg2://{user}:{password}@localhost/{db}'.format(
        user=DB_USER, password=DB_PASSWORD, db=DB_NAME)

DEBUG = 'DEBUG' in os.environ
print('DEBUG:%s'%DEBUG)

APP_SERVE_STATIC = 'APP_SERVE_STATIC' in os.environ
print('APP_SERVE_STATIC:%s'%APP_SERVE_STATIC)

POLL_PERIOD = 120

MAX_HISTORY = 24*30  # max history in hours

API_VERSION = 6

MAILGUN_API_KEY = CREDENTIALS['mailGunApiKey']

# ADD/OVERWRITE WITH MACHINE LOCAL CONFIGS
try:
    from config_local import *
except ImportError as e:
    print("No local config file found. If you want to override configs for " \
              "this machine, create /src/server/config_local.py")

