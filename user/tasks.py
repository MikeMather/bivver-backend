from __future__ import absolute_import, unicode_literals
from utils.utils import get_sendgrid_html
from celery.decorators import task
from utils.mail import Mail


@task
def send_verification_email(verify_url, email, verification_token):
        subject = 'Welcome to Vinocount! Verify your email'
        verification_url = '{}verify/?token={}'.format(verify_url, verification_token)
        context = {
            'verify_url': verification_url
        }
        html = html = get_sendgrid_html('VERIFY_EMAIL')
        email = Mail(subject, [email])
        email.render_template(html, context)
        email.send()