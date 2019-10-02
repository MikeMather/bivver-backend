from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import status, viewsets, generics, permissions, mixins
from rest_framework.response import Response
from .filters import *

class SupplierListViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Supplier.objects.all().prefetch_related('user__shipping_address', 'items')
    serializer_class = SupplierSerializer
    filterset_class = SupplierFilter
    permission_classes = (permissions.AllowAny,)
