from django_filters import *
from datetime import datetime, timedelta
from django.db.models import Q
from .models import *


class SupplierFilter(FilterSet):
    name = CharFilter(lookup_expr='icontains', field_name='name')
    country = CharFilter(field_name='name', label='country', method='filter_country')
    region = CharFilter(field_name='name', label='region', method='filter_region')

    class Meta:
        model = Supplier
        fields = {
            'id': ['exact']
        }

    def filter_country(self, queryset, name, value):
        return queryset.filter(user__shipping_address__country=value)
    
    def filter_region(self, queryset, name, value):
        return queryset.filter(user__shipping_address__region=value)