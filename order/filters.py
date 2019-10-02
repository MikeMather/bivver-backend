from django_filters import FilterSet, DateFromToRangeFilter, BooleanFilter
from datetime import datetime, timedelta
from django.db.models import Q
from .models import *


class OrderFilter(FilterSet):
    updated_at = DateFromToRangeFilter()
    supplier_active = BooleanFilter(field_name='status', label='is_supplier_active', method='filter_supplier_active')
    pending_delivery = BooleanFilter(field_name='status', label='pending_delivery', method='filter_pending_delivery')
    client_active = BooleanFilter(field_name='status', label='is_client_active', method='filter_client_active')

    class Meta:
        model = Order
        fields = {
            'client': ['exact'], 
            'supplier': ['exact'],
            'updated_at': ['exact', 'lt', 'gt', 'isnull'],
            'state': ['exact']
        }
    
    def filter_supplier_active(self, queryset, name, value):
        active_supplier_states = [
            'pending_payment', 
            'paid', 
            'received', 
            'supplier_editing', 
            'pending_supplier_approval', 
            'delivered_paid', 
            'delivered_pending_payment',
            'pending_client_approval',
            'declined'
        ]
        return queryset.filter(state__in=active_supplier_states)
    
    def filter_client_active(self, queryset, name, value):
        active_client_states = [
            'pending_payment', 
            'paid', 
            'supplier_editing', 
            'pending_supplier_approval',
            'pending_client_approval',
            'declined',
            'draft'
        ]
        return queryset.filter(state__in=active_client_states)

    def filter_pending_delivery(self, queryset, name, value):
        return queryset.filter(state__in=['pending_payment', 'paid'])


class LineItemFilter(FilterSet):

    class Meta:
        model = LineItem
        fields = {
            'order': ['exact']
        }

class OrderActivityFilter(FilterSet):

    class Meta:
        model = OrderActivity
        fields = {
            'order': ['exact']
        }