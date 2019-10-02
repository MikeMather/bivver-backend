from rest_framework import serializers
from .models import *
from order.serializers import *


class ClientSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(required=False, many=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Client
        exclude = ('user',)