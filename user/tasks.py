from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from utils.mail import Mail


@task
def send_verification_email(verify_url, email, verification_token):
        subject = 'Welcome to Vinocount! Verify your email'
        verification_url = '{}verify/?token={}'.format(verify_url, verification_token)
        email = Mail(subject, [email])
        email.render_string('verifyEmail.html', {'verification_url': verification_url})
        email.send()


