from django_filters import *
from datetime import datetime, timedelta
from django.db.models import Q
from .models import *


class ItemFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains', field_name='name')

    class Meta:
        model = Item
        fields = {
            'discounted_price': ['gt'],
            'created_at': ['gt'],
            'supplier': ['exact']
        }