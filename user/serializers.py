from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import *
from supplier.serializers import *
from client.serializers import *


class AddressSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Address
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(required=False)
    client = ClientSerializer(required=False)
    shipping_address = AddressSerializer(required=False)
    billing_address = AddressSerializer(required=False)
    has_payment_account = serializers.SerializerMethodField()
    addresses_are_same = serializers.BooleanField(write_only=True, required=False)

    def get_has_payment_account(self, obj):
        try:
            has_account = obj.payment_account is not None
            return has_account
        except ObjectDoesNotExist:
            return False

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'supplier', 'client', 'shipping_address', 
        'verified', 'billing_address', 'account_type', 'has_payment_account', 'addresses_are_same')
    

class PaymentAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentAccount
        fields = '__all__'