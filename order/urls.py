from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'line-items', LineItemViewSet, basename='line-items')

urlpatterns = [
    path('', include(router.urls)),
    path('tax-rates/<int:clientId>/', tax_rates, name='tax-rates'),
    path('order-activities/', OrderActivityViewSet.as_view(), name='order-activities'),
    path('payments/', PaymentsViewSet.as_view(), name='payments'),
    path('activities-seen/', mark_activities_seen, name='mark-activities-seen'),
    path('signatures/<int:orderId>/', retrieve_signature_image, name='signatures'),
    path('invoices/<int:orderId>/', retrieve_invoice_pdf, name='invoice-pdfs'),
]
