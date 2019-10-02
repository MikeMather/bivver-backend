from .main import *
import sentry_sdk

sentry_sdk.init("https://d67c6bd7bd1b41c4a41419346f7181f4@sentry.io/1481389")

DEBUG = True
SCOUT_NAME = 'Vinocount Staging'