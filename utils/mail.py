from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.utils.html import strip_tags
from django.template.loader import render_to_string


class Mail:

    def __init__(self, subject, to_emails, html=None):
        self.subject = subject
        self.to_emails = to_emails
        self.from_email = settings.FROM_EMAIL
        self.html = html
        self.text = strip_tags(html)

    def render_template(self, template, context={}):
        template = Template(template)
        self.html = template.render(Context(context))
        self.text = strip_tags(self.html)

    def render_string(self, template_path, context):
        self.html = render_to_string(template_path, context)

    def send(self, attachments=[]):
        msg = EmailMultiAlternatives(self.subject, self.text, self.from_email, self.to_emails)
        msg.attach_alternative(self.html, 'text/html')
        for attachment in attachments:
            msg.attach(attachment['filename'], attachment['data'], attachment['content-type'])
        msg.send()
