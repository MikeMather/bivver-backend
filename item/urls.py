from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='item')
router.register(r'browse', ItemListViewSet, basename='browse-items')

urlpatterns = [
    path('', include(router.urls))
]
