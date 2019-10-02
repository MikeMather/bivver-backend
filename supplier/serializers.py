from rest_framework import serializers
from .models import *
from django.core.exceptions import ObjectDoesNotExist


class SupplierSerializer(serializers.ModelSerializer):
    contact_email = serializers.CharField(source='user.email', required=False)
    address =  serializers.CharField(source='user.shipping_address.address', required=False)
    city =  serializers.CharField(source='user.shipping_address.city', required=False)
    region =  serializers.CharField(source='user.shipping_address.region', required=False)
    accepts_card_payments = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Supplier
        exclude = ('user',)

    def get_accepts_card_payments(self, obj):
        try:
            payment_account = obj.user.payment_account
            return True
        except ObjectDoesNotExist:
            return False
