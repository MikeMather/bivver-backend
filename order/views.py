from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework import status, viewsets, generics, permissions
from djangorestframework_fsm.viewset_mixins import get_drf_fsm_mixin
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .filters import *
from .permissions import *
from utils.utils import get_tax
from utils.payments import PaymentManager
import stripe


# paginate the invoices to reduce query size
class OrderResultsPagination(PageNumberPagination):
    page_size = 15
    pag_size_query_param = 'page_size'
    max_page_size = 1000


class OrderViewSet(get_drf_fsm_mixin(Order), viewsets.ModelViewSet):

    queryset = Order.objects.all().prefetch_related('line_items', 'supplier', 'activities__user__client', 'activities__user__supplier')
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    permission_classes = [OrderPermissions]

    def create(self, request):
        if request.user.account_type != 'client':
            return Response({'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)
        return super().create(request)
        

class LineItemViewSet(viewsets.ModelViewSet):

    queryset = LineItem.objects.all().prefetch_related('item').select_related('order')
    serializer_class = LineItemSerializer
    permission_classes = [LineItemPermissions]


@api_view(['GET'])
def tax_rates(request, clientId):
    """
        Get the tax rate using the country and region of a given location
    """
    client = Client.objects.get(pk=clientId)
    address = client.user.shipping_address
    try:
        tax_rate = get_tax(address.country, address.region)
        return Response({'hst': tax_rate}, status.HTTP_200_OK)
    except ValueError:
        return Response({'message': 'Tax details unavailable'}, status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def mark_activities_seen(request):
    """
        Mark order activities as seen
    """
    order = Order.objects.get(pk=request.data['order'])
    if order.client.user == request.user:
        activities = OrderActivity.objects.filter(order=order).update(client_seen=True)
    elif order.supplier.user == request.user:
        activities = OrderActivity.objects.filter(order=order).update(supplier_seen=True)
    return Response(status.HTTP_200_OK)


@api_view(['GET'])
def retrieve_signature_image(request, orderId):
    """
        Generate a presigned url for an invoice signature from S3
    """

    order = Order.objects.get(pk=orderId)
    
    # Check that the user has access
    if not (order.client.user == request.user or order.supplier.user == request.user):
        return Response({'message': 'You don\'t have access to this resource'}, status.HTTP_401_UNAUTHORIZED)

    key = order.signature_key
    if not key:
        return Response({'message': 'Signature not found'}, status.HTTP_404_NOT_FOUND)    
    client = S3Client(settings.AWS_VINOCOUNT_IMAGES_BUCKET_NAME)
    link = client.get_presigned_url(key)
    return Response({'url': link}, status.HTTP_200_OK)


class OrderActivityViewSet(generics.CreateAPIView):

    queryset = OrderActivity.objects.all()
    serializer_class = OrderActivitySerializer

    def create(self, request):
        activity_data = {
            'order': request.data['order'],
            'user': request.user.id,
            'message': request.data['message'],
            'client_seen': request.data.get('client_seen', False),
            'supplier_seen': request.data.get('supplier_seen', False),
            'activity': request.data.get('activity', '')
        }
        activity_serializer = OrderActivitySerializer(data=activity_data)
        if activity_serializer.is_valid():
            activity_serializer.save()
            return Response(activity_serializer.data, status.HTTP_201_CREATED)
        else:
            return Response(activity_serializer.errors, status.HTTP_400_BAD_REQUEST)


class PaymentsViewSet(generics.CreateAPIView):

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request):

        stripe.api_key = settings.STRIPE['CLIENT_SECRET']

        supplier_id = request.data['supplier']
        order_id = request.data['order']
        amount = int(float(request.data['amount']) * 100)
        payment_method = request.data['payment_method'].lower()
        deferred = request.data['deferred']
        token = request.data.get('token', None)
        
        supplier = Supplier.objects.get(pk=supplier_id)
        order = Order.objects.get(pk=order_id)
        payments = PaymentManager(supplier_id, order.client_id)

        if order.payment and not token:
            payment = order.payment
            # Update payment intent in stripe in case amount changed
            if not payment.payment_type == payment_method:
                OrderActivity.objects.create(
                    order=order,
                    user=request.user,
                    activity='Payment change',
                    message=f'Payment method changed from {payment.payment_type} to {payment_method}'
                )
            payment.payment_type = payment_method
            payment.amount = amount
            payment.save()
            return Response({'message': 'Payment successfully updated'}, status.HTTP_200_OK)
        else:
            try:
                if token and not hasattr(request.user, 'payment_account'): # First time user is submitting invoice, need to create a customer for them
                    payments.create_shared_customer(token)
                
                if not order.payment:
                    intent = payments.create_payment_intent(amount, payment_method, deferred)
                    order.payment_id = intent.pk
                    order.save()
                
                return Response({'message': 'Payment successfully created'}, status.HTTP_200_OK)
            except ObjectDoesNotExist:
                return Response({'message': 'Supplier does not support card payments'}, status.HTTP_200_OK)