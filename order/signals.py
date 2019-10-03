from django.db.models.signals import *
from django.dispatch import receiver
from order.models import *
from django_fsm.signals import *
from order.tasks import *
from celery import chain
from django.db import transaction


@receiver([post_transition], sender=Order)
def handle_invoice_transition(sender, instance, *args, **kwargs):
    # Save the instance so that we know the instance being retrieved by the Celery tasks is the most updated
    instance.save()
    if kwargs['name'] in ['deliver_pending_payment', 'deliver']:
        # Generate the invoice pdf and email it to clients on delivery
        # Use on_commit to only execute once the above save() is commited to the db
        transaction.on_commit(lambda: generate_invoice_pdf.apply_async((instance.id,), link=email_order_delivered.s(instance.id)))
    else:
        transaction.on_commit(lambda: generate_invoice_pdf.delay(instance.id))
        