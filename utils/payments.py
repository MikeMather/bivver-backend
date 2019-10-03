import stripe
from supplier.models import Supplier
from order.models import Payment, Order
from user.models import PaymentAccount
from django.conf import settings
from client.models import Client
from django.core.exceptions import ObjectDoesNotExist

class PaymentManager:

    def __init__(self, supplier_id, client_id):
        stripe.api_key = settings.STRIPE['CLIENT_SECRET']
        self.supplier = Supplier.objects.get(pk=supplier_id)
        self.supplier_user = self.supplier.user
        self.client = Client.objects.get(pk=client_id)
        self.client_user = self.client.user

    
    def create_shared_customer(self, token):
        """
        Creates a shared customer between us (platform account) and the connect account (suppliers)
        allowing us to invoice customers on the suppliers behalf
        """
        customer = stripe.Customer.create(
            description=self.client.name,
            source=token,
            stripe_account=self.supplier_user.payment_account.stripe_user_id
        )
        PaymentAccount.objects.create(
            stripe_user_id=customer.id,
            user=self.client_user
        )
        return customer

    
    def create_payment_intent(self, amount, payment_method, deferred):
        """
        Create a payment intent between a supplier's connect account and their customer
        """
        payment = Payment(
            amount=amount,
            captured=False,
            payment_type=payment_method,
            deferred=deferred
        )
        payment.save()
        return payment

    def create_charge(self, payment):
        """
        Capture the payment of a payment intent
        """
        if payment and not payment.captured and payment.payment_type == 'card':
            fees = int(payment.amount * settings.STRIPE['APPLICATION_FEE'])
            payment_intent = stripe.Charge.create(
                amount=payment.amount,
                currency='cad',
                application_fee_amount=fees,
                stripe_account=self.supplier_user.payment_account.stripe_user_id,
                customer=self.client_user.payment_account.stripe_user_id,
            )
            payment.charge_id = payment_intent['id']
            payment.captured = True
            payment.save()
