from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from utils.constants import ACCOUNT_TYPES
from supplier.models import Supplier
from client.models import Client
from bcrypt import hashpw, checkpw, gensalt


class User(AbstractUser):
    verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=300, blank=True, default='')
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES.CHOICES, default=ACCOUNT_TYPES.CHOICES[0][0])
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, related_name="shipping_location", null=True)
    billing_address = models.ForeignKey('Address', on_delete=models.SET_NULL, related_name="billing_location", null=True)

    def set_password(self, raw_password):
        hashed_pw = hashpw(raw_password.encode('utf-8'), gensalt())
        self.password = hashed_pw.decode('utf-8')

    class Meta:
        db_table = 'users'


class PaymentAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_account")
    stripe_user_id = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
            db_table = 'payment_accounts'


class VerificationToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tokens")
    token = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now=True)

    @property
    def is_expired(self):
        return (datetime.now(timezone.utc) - self.created_at) > settings.VERIFICATION_TOKEN_EXPIRATION

    def generate(self):
        new_token = token_urlsafe(32)
        self.token = hashpw(new_token.encode('utf-8'), gensalt()).decode('utf-8')
        self.save()
        return new_token

    def match(self, token):
        return checkpw(token.encode('utf-8'), self.token.encode('utf-8'))

    class Meta:
        db_table = 'verification_tokens'


class Address(models.Model):
    address = models.CharField(max_length=500, blank=True)
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'addresses'
        verbose_name_plural = "Addresses"