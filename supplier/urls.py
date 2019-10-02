from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'search', SupplierListViewSet, basename='browse-suppliers')

urlpatterns = [
    path('', include(router.urls)),
]
