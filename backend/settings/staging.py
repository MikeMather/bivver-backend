from .main import *
import sentry_sdk

sentry_sdk.init("https://b4473b9cb8974d308bd969d791a3c7b9@sentry.io/1770567")

DEBUG = True
SCOUT_NAME = 'Bivver Staging'