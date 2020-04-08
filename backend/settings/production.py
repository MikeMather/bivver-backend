from .main import *
import sentry_sdk
import os

sentry_sdk.init("https://<sentrykey>@sentry.io")

DEBUG = False

EMAIL_BACKEND = 'django_ses.SESBackend'
FROM_EMAIL = 'noreply@fytics.com'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = '587'

# Stripe keys
STRIPE = {
    'API_KEY': os.environ.get('STRIPE_API_KEY', ''),
    'CLIENT_SECRET': os.environ.get('STRIPE_SECRET', ''),
    'CLIENT_ID': '',
    'TOKEN_URL': 'https://connect.stripe.com/oauth/token',
    'APPLICATION_FEE': 0.01,
}
