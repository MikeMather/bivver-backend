from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import status, viewsets, generics, permissions
from rest_framework.response import Response
from .filters import *


class ItemViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        return Item.objects.all()

    serializer_class = ItemSerializer
    filterset_class = ItemFilter

    def create(self, request):
        if request.user.account_type != 'supplier':
            return Response({'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)
        return super().create(request)


class ItemListViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Item.objects.filter(disabled=False)
    serializer_class = ItemSerializer
    filterset_class = ItemFilter
    permission_classes = (permissions.AllowAny,)