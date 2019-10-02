from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterViewSet.as_view(), name='register'),
    path('user/', UserViewSet.as_view(), name='user'),
    path('verify/', EmailVerify.as_view(), name='verify'),
    path('settings/<int:pk>/', UserSettingsViewSet.as_view(), name='settings'),
    path('payment-token/<int:userId>/', get_stripe_token, name='stripe-token'),
    path('payment-account/', create_payment_account, name='payment-account'),
]
