from __future__ import absolute_import, unicode_literals
from celery.decorators import task
from django.conf import settings
from utils.utils import get_tax
from item.models import *
from datetime import timedelta
from utils.pdf_manager import PdfManager
from utils.utils import get_sendgrid_html
from decimal import Decimal
from utils.aws import S3Client
import re
import json


def send_order_email(subject, to_emails, context, template, attachment=None):
        from utils.mail import Mail
        email = Mail(subject, to_emails)
        email.render_template(template, context)
        if attachment:
            email.send(attachments=[attachment])
        else:
            email.send()

@task
def email_client_submit(order_id):
        from order.models import Order
        order = Order.objects.get(pk=order_id)
        subject = 'New Order'
        order_url = '{}orders/{}'.format(settings.SUPPLIER_FRONTEND_URL, order.id)
        to_email = order.supplier.user.email
        context = {
            'client_name': order.client.name,
            'order_url': order_url,
        }
        html = get_sendgrid_html('ORDER_SUBMIT')
        send_order_email(subject, [to_email], context, html)


@task
def email_order_approved(order_id):
        from order.models import Order
        order = Order.objects.get(pk=order_id)
        subject = 'Order approved by {}'.format(order.supplier.name)
        redirect_url = '{}orders/{}'.format(settings.CLIENT_FRONTEND_URL, order.id)
        to_emails = order.client.user.email
        context = {
            'supplier': order.supplier.name,
            'order_url': redirect_url
        }
        html = html = get_sendgrid_html('ORDER_APPROVE')
        send_order_email(subject, [to_emails], context, html)


@task
def email_order_declined(order_id):
        from order.models import Order

        order = Order.objects.get(pk=order_id)
        subject = 'Order for {} declined'.format(order.supplier.name)
        redirect_url = '{}orders/{}'.format(settings.CLIENT_FRONTEND_URL, order.id)
        to_emails = order.client.user.email
        context = {
            'supplier_name': order.supplier.name,
            'order_url': redirect_url
        }
        html = html = get_sendgrid_html('ORDER_DECLINE')
        send_order_email(subject, [to_emails], context, html)


@task
def email_order_revision_requested(order_id):
        from order.models import Order

        order = Order.objects.get(pk=order_id)
        subject = 'Revision requested for an order'
        redirect_url = '{}orders/{}'.format(settings.CLIENT_FRONTEND_URL, order.id)
        to_email = order.client.user.email
        last_activity = order.activities.last()
        context = {
            'order_id': order.id,
            'supplier_name': order.supplier.name,
            'order_url': redirect_url,
            'activity_message': last_activity.message
        }
        html = html = get_sendgrid_html('ORDER_REVISE')
        send_order_email(subject, [to_email], context, html)


@task
def email_order_delivered(filename, order_id):
        from order.models import Order

        order = Order.objects.get(pk=order_id)
        subject = 'Order Completed'
        to_emails = [order.client.user.email, order.supplier.user.email]
        updated_at = order.updated_at.strftime('%Y-%m-%d')
        context = {
            'supplier_name': order.supplier.name,
            'updated_at': updated_at
        }
        if order.pdf_key:
            client = S3Client(settings.AWS_VINOCOUNT_IMAGES_BUCKET_NAME)
            pdf = client.download_object(order.pdf_key)
            attachment = {
                'filename': filename,
                'data': pdf.read(),
                'content-type': 'application/pdf'
            }
            html = html = get_sendgrid_html('ORDER_DELIVER')
            send_order_email(subject, to_emails, context, html, attachment=attachment)
            

# Remove the order quantities for an order from the supplier's inventory
@task
def update_supplier_inventory(order_id):
    from order.models import Order
    order = Order.objects.get(pk=order_id)
    for line_item in order.line_items.all():
        if line_item.item.stock_quantity > line_item.order_quantity:
            new_quantity = line_item.item.stock_quantity - line_item.order_quantity
            line_item.item.stock_quantity = new_quantity
        else:
            # If they don't have enough in stock to fill the order, just set the item's quantity to 0
            line_item.item.stock_quantity = 0
        line_item.item.save()


@task
def generate_invoice_pdf(order_id):
    from order.models import Order
    order = Order.objects.get(pk=order_id)
    if order.pdf_key:
        client = S3Client(settings.AWS_VINOCOUNT_IMAGES_BUCKET_NAME)
        client.delete_object(order.pdf_key)

    line_items = []
    keg_deposits = 0
    for i in order.line_items.all():
        line_items += [{'line_item': i, 'cost': round(i.price*i.order_quantity, 2)} ]
        if i.item.order_by == 'Keg':
            keg_deposits += i.order_quantity

    # Calculate total values
    is_paid =  order.state == 'paid' or order.state == 'delivered_paid'
    tax_rate = get_tax(order.client.user.shipping_address.country, order.client.user.shipping_address.region)
    total_before_tax = float(sum([item.price * item.order_quantity for item in order.line_items.all()]))
    total_due = order.payment.amount / 100
    keg_deposit_price = order.supplier.keg_deposit_price

    # The data to be displayed in the order
    context = {
        'order': order,
        'line_items': line_items,
        'supplier': order.supplier,
        'supplier_user': order.supplier.user,
        'client': order.client,
        'issue_date': order.payment_due_date - timedelta(days=order.supplier.default_payment_term),
        'payment_status': 'Paid' if is_paid else 'Outstanding',
        'amount_due': 0 if is_paid else '%.2f' % total_due,
        'tax': tax_rate * 100,
        'taxed_subtotal': '%.2f' % round(tax_rate * total_before_tax, 2),
        'subtotal': '%.2f' % total_before_tax,
        'total': '%.2f' % total_due,
        'amount_paid': '%.2f' % total_due if is_paid else 0,
        'keg_deposits': keg_deposits,
        'keg_deposits_cost': '%.2f' % round(keg_deposit_price * keg_deposits, 2),
        'keg_returns_cost': '-%.2f' % round(keg_deposit_price * order.keg_returns, 2)
    }

    # Generating the pdf saves it to S3 and returns the key in the bucket
    pdf_generator = PdfManager('invoicePdf.html', context)
    client_name = re.sub(r'[^\w\s]', '', order.client.name).replace(' ', '_')
    filename = 'Order{}_{}.pdf'.format(order.id, client_name)
    key = pdf_generator.generate(filename)
    order.pdf_key = key
    order.save()
    return filename


