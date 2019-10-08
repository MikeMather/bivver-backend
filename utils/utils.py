from django.contrib.auth.models import Group
from sendgrid import SendGridAPIClient
from django.db.models import Max
from django.conf import settings
from item.models import *
from user.models import *
from django.core.cache import cache
from utils.aws import S3Client
from utils.constants import *
import stripe
import requests
import base64
import json
import io
import boto3
import uuid
import re


def add_stripe_subscription(location, type, token):
    location_settings = location.settings
    stripe.api_key = settings.STRIPE['CLIENT_SECRET']
    if not location_settings.stripe_id:
        customer = stripe.Customer.create(
            name=location.name,
            source=token
        )
        location_settings.stripe_id = customer.id
        location_settings.save()
        stripe.Subscription.create(customer=customer.id,
                                   items=[{'plan': settings.STRIPE['PLANS'][type], 'quantity': 1}])
    else:
        customer = stripe.Customer.retrieve(location_settings.stripe_id)
        subscriptions = customer['subscriptions']['data']
        subscription_id = None
        for subscription in subscriptions:
            if subscription['plan']['id'] == settings.STRIPE['PLANS'][type]:
                subscription_quantity = subscription['quantity'] + 1
                subscription_id = subscription['id']
                stripe.Subscription.modify(subscription_id, quantity=subscription_quantity)
        if subscription_id is None:
            stripe.Subscription.create(customer=customer.id,
                                       items=[{'plan': settings.STRIPE['PLANS'][type], 'quantity': 1}])


def process_image(base64_image_string, folder, name=None, delete_key=None):
    image_string = base64.b64decode(base64_image_string)
    bucket = settings.AWS_S3_URL
    if not name:
        key = str(uuid.uuid4())[:8]
    else:
        key = "".join(re.findall('[a-zA-Z]+', name))
    file_name = '{0}/{1}.jpg'.format(folder, key)
    image_url = bucket + file_name

    client = S3Client(settings.AWS_VINOCOUNT_IMAGES_BUCKET_NAME)

    if delete_key:
        client.delete_object(delete_key)
    data = io.BytesIO(image_string)
    data.seek(0)
    client.upload_image(data, file_name)

    return file_name


def format_date(datetime):
    return datetime.strftime(settings.DATETIME_FORMAT)


def get_tax(country, region):
    country = country.lower()
    region = region.lower()
    if country and region:
        region_code = settings.TAX_API[country]['regions'][region]
        endpoint = settings.TAX_API[country]['endpoint'] + region_code
        response = requests.get(endpoint)
        return float(response.json()['hst'])
    else:
        raise ValueError('Country and region are required')

def get_active_orders_list(user):
    if user.account_type == 'supplier':
        return SUPPLIER_ACTIVE_ORDER_STATES
    return CLIENT_ACTIVE_ORDER_STATES
    

def get_sendgrid_html(key):
    sg = SendGridAPIClient(settings.SENDGRID['API_KEY'])
    response = sg.client.templates._(settings.SENDGRID['TEMPLATES'][key]).get()
    return json.loads(response.body)['versions'][0]['html_content']