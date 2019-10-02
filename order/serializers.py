from rest_framework import serializers
from .models import *
from supplier.serializers import *
from item.serializers import *
from client.models import *
from utils.aws import S3Client
import secrets
import io
import base64


class SimpleClientSerializer(serializers.ModelSerializer):
    contact_email = serializers.CharField(source='user.email', required=False)
    address =  serializers.CharField(source='user.shipping_address.address', required=False)
    city =  serializers.CharField(source='user.shipping_address.city', required=False)
    region =  serializers.CharField(source='user.shipping_address.region', required=False)

    class Meta:
        model = Client
        fields = '__all__'


class LineItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = LineItem
        fields = '__all__'


class OrderActivitySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = OrderActivity
        fields = '__all__'

    def get_name(self, obj):
        try:
            return obj.user.client.name
        except ObjectDoesNotExist:
            return obj.user.supplier.name
    
    def get_image(self, obj):
        try:
            return obj.user.client.image
        except ObjectDoesNotExist:
            return obj.user.supplier.image


class OrderSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    client = SimpleClientSerializer(read_only=True)
    line_items = LineItemSerializer(many=True, read_only=True)
    activities = OrderActivitySerializer(many=True, required=False)
    supplier_id = serializers.IntegerField(write_only=True)
    client_id = serializers.IntegerField(write_only=True)
    payment_method = serializers.CharField(source='payment.payment_type', required=False)
    amount_due = serializers.IntegerField(source='payment.amount', required=False)
    payment_deferred = serializers.BooleanField(source='payment.deferred', required=False)
    signature_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'payment' in validated_data:
            if instance.payment:
                payment = validated_data.pop('payment')
                instance.payment.payment_type = payment.get('payment_type', instance.payment.payment_type)
                instance.payment.amount = payment.get('amount', instance.payment.amount)
                instance.payment.save()

        # If the delivery comes with a signature (as base64) upload it to S3 as an image and save the key
        if 'signature_base64' in validated_data and not instance.signature_key:
            signature = validated_data.pop('signature_base64', None)
            if signature:
                signature_string = base64.b64decode(signature)

                folder = 'invoice-signatures'
                file_name = '{0}/{1}.jpg'.format(folder, secrets.token_urlsafe())

                client = S3Client(settings.AWS_VINOCOUNT_IMAGES_BUCKET_NAME)
                data = io.BytesIO(signature_string)
                data.seek(0)
                client.upload_object(data, file_name, 'image/jpeg')
                instance.signature_key = file_name

        return super().update(instance, validated_data)

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'
