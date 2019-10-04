from .main import *
import sentry_sdk
import os

sentry_sdk.init("https://20e1ed68bf424fe0ad46a8b428067e89@sentry.io/1468907")

DEBUG = False

EMAIL_BACKEND = 'django_ses.SESBackend'
FROM_EMAIL = 'noreply@fytics.com'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = '587'

# Stripe keys
STRIPE = {
    'API_KEY': os.environ.get('STRIPE_API_KEY', 'pk_test_BJHlY3dKiWDpjGVihty1Zwm9'),
    'CLIENT_SECRET': os.environ.get('STRIPE_SECRET', 'sk_test_4JxNtbEsWhtvC1pWHaYDCB4b'),
    'CLIENT_ID': 'ca_Ehf6RukQblf1Rg23P0cHAdmBYs7cDGny',
    'TOKEN_URL': 'https://connect.stripe.com/oauth/token',
    'APPLICATION_FEE': 0.01,
}