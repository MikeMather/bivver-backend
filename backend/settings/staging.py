from .main import *
import sentry_sdk

sentry_sdk.init("https://@sentry.io/")

DEBUG = True
SCOUT_NAME = 'Bivver Staging'
