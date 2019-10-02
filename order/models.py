from django.db import models
from django.core.validators import MinValueValidator
from client.models import *
from supplier.models import *
from django_fsm import FSMField, transition
from item.models import *
from django.conf import settings
from datetime import datetime


class Payment(models.Model):
    amount = models.IntegerField(validators=[MinValueValidator(0)], null=False, blank=False, default=0)
    payment_type = models.CharField(max_length=300, null=True, blank=True)
    charge_id = models.CharField(max_length=500, null=True, blank=True)
    captured = models.BooleanField(default=False) # Indicates whether we've processed our application fees
    deferred = models.BooleanField(default=False) # Indicates whether the user wants to defer processing the payment 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, on_delete=models.SET_NULL, related_name='orders')
    order_verification_token = models.CharField(max_length=100, blank=True)
    payment_due_date = models.DateField(blank=True, null=True, default=None)
    state = FSMField(default='draft')
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='order', null=True)
    delivered_at = models.DateTimeField(blank=True, null=True, default=None)
    submitted_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pdf_key = models.CharField(max_length=300, null=True, blank=True)
    keg_returns = models.IntegerField(validators=[MinValueValidator(0)], null=False, blank=False, default=0)
    signature_key = models.CharField(max_length=1500, null=True, blank=True)

    @transition(field=state, source=['draft', 'pending_client_approval'], target='pending_supplier_approval')
    def client_submit(self):
        from order.tasks import email_client_submit
        self.submitted_at = datetime.now()
        self.save()
        email_client_submit.delay(self.id)
        # If location isn't already a client, add to supplier's client list
        # self.client.create_supplier_client(self.supplier)
    
    @transition(field=state, source='pending_supplier_approval', target='pending_client_approval')
    def supplier_submit(self):
        from order.tasks import email_order_revision_requested
        email_order_revision_requested.delay(self.id)
    
    @transition(field=state, source=['pending_supplier_approval'], target='paid')
    def supplier_approve(self):
        from order.tasks import update_supplier_inventory, email_order_approved
        self.create_activity('Approved', created_by='supplier')
        email_order_approved.delay(self.id)
        # update_supplier_inventory.delay(self.id) # Remove quantities from supplier's inventory
    
    @transition(field=state, source=['pending_supplier_approval'], target='pending_payment')
    def supplier_approve_unpaid(self):
        from order.tasks import update_supplier_inventory
        self.create_activity('Approved', created_by='supplier')
        # Create client if not already a client
        # self.client.create_supplier_client(self.supplier)
        # email_order_approved.delay(self.id)
        # update_supplier_inventory.delay(self.id)

    @transition(field=state, source=['pending_payment', 'draft'], target='paid')
    def client_paid(self):
        from utils.payments import PaymentManager
        payments = PaymentManager(self.supplier_id, self.client_id)
        payments.create_charge(self.payment)
        self.create_activity('Order paid', created_by='supplier')
    
    @transition(field=state, source=['pending_payment'], target='delivered_pending_payment')
    def deliver_pending_payment(self):
        self.create_activity('Delivered', created_by='supplier')

    @transition(field=state, source=['delivered_pending_payment'], target='delivered_paid')
    def deliver_paid(self):
        from utils.payments import PaymentManager
        payments = PaymentManager(self.supplier_id, self.client_id)
        payments.create_charge(self.payment)
        self.create_activity('Order paid', created_by='supplier')

    @transition(field=state, source=['paid'], target='delivered_paid')
    def deliver(self):
        from utils.payments import PaymentManager
        self.create_activity('Delivered', created_by='supplier')
        payments = PaymentManager(self.supplier_id, self.client_id)
        payments.create_charge(self.payment)

    @transition(field=state, source=['pending_supplier_approval'], target='declined')
    def decline(self):
        from order.tasks import email_order_declined
        email_order_declined.delay(self.id)

    class Meta:
        db_table = 'orders'
        ordering = ('-submitted_at',)

    def create_activity(self, title, created_by='client'):
        OrderActivity.objects.create(
            user=(self.client.user if created_by == 'client' else self.supplier.user),
            order=self,
            activity=title,
            client_seen=(created_by == 'client'),
            supplier_seen=(created_by == 'supplier')
        )

class LineItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='line_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='line_items')
    order_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=32, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('item', 'order')
        db_table = 'line_items'


class OrderActivity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_activities')
    activity = models.CharField(max_length=150, blank=True, default='')
    message = models.CharField(max_length=500, blank=True, default='')
    client_seen = models.BooleanField(default=False)
    supplier_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_activities'
        verbose_name_plural = "Order Activities"
        ordering = ('created_at',)