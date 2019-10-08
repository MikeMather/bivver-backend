from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from secrets import token_urlsafe
from user.tasks import send_verification_email
from utils.utils import process_image, get_active_orders_list
from client.serializers import *
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
import stripe
import requests
from django.db.models import Prefetch


class UserViewSet(generics.RetrieveAPIView):

    def get_object(self):
        return User.objects.filter(pk=self.request.user.id)\
            .prefetch_related('shipping_address', 
            'billing_address',
            Prefetch('client__orders', queryset=Order.objects.filter(state__in=get_active_orders_list(self.request.user)).prefetch_related('line_items__item')),
            )\
            .select_related('supplier', 'payment_account')\
            .first()
        
    serializer_class = UserSerializer


class RegisterViewSet(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        account_type = request.data['account_type']
        username = request.data['username']
        password = request.data['password']
        name = request.data['name']
        verification_token = token_urlsafe(16)

        image = ''
        if 'image' in request.data:
            image = process_image(request.data['image'], 'users')

        user_data = {
            'email': username,
            'username': username,
            'password': password,
            'account_type': account_type,
        }
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(password)
            user.verification_token = verification_token
        else:
            return Response(user_serializer.errors, status.HTTP_400_BAD_REQUEST)

        address_data = {
            'address': request.data['address'],
            'city': request.data['city'],
            'country': request.data['country'],
            'region': request.data['region'],
            'postal_code': request.data['postal_code']
        }
        address_serializer = AddressSerializer(data=address_data)
        if address_serializer.is_valid():
            address = address_serializer.save()
            user.shipping_address = address
            user.billing_address = address
        else:
            user.delete()
            return Response(address_serializer.errors, status.HTTP_400_BAD_REQUEST)        

        if account_type == 'supplier':
            try:
                existing_supplier = Supplier.objects.get(name=name)
                return Response({'message': 'A supplier with that name already exists'}, status.HTTP_400_BAD_REQUEST)
            except ObjectDoesNotExist:
                pass

            email_verify_url = settings.SUPPLIER_FRONTEND_URL
            supplier_data = {
                'default_payment_term': request.data['default_payment_term'],
                'keg_deposit_price': 0,
                'user_id': user.id,
                'name': name,
                'image': image,
            }
            supplier_serializer = SupplierSerializer(data=supplier_data)
            if supplier_serializer.is_valid():
                supplier = supplier_serializer.save()
            else:
                user.delete()
                address.delete()
                return Response(supplier_serializer.errors, status.HTTP_400_BAD_REQUEST)
        else:
            email_verify_url = settings.CLIENT_FRONTEND_URL
            client_data = {
                'licensee_number': request.data['licensee_number'],
                'user_id': user.id,
                'name': name,
                'image': image,
            }
            client_serializer = ClientSerializer(data=client_data)
            if client_serializer.is_valid():
                client_serializer.save()
            else:
                user.delete()
                address.delete()
                return Response(client_serializer.errors, status.HTTP_400_BAD_REQUEST)

        user.save()
        send_verification_email.delay(email_verify_url, user.email, user.verification_token)
        return Response({'message': 'User successfully created'}, status.HTTP_201_CREATED)


class EmailVerify(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        if 'token' in request.data:
            token = request.data['token']
            user = User.objects.get(verification_token=token)
            user.verified = True
            user.save()
            return Response({'message': 'Your email has been verified!'}, status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid Token'}, status.HTTP_400_BAD_REQUEST)


class UserSettingsViewSet(generics.UpdateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def patch(self, request, pk):

        user = User.objects.get(pk=pk)
        if user.id != request.user.id:
            return Response({'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)
        
        user.username = request.data['username']
        user.email = request.data['email']


        shipping_address_data = request.data['shipping_address']
        billing_address_data = request.data['billing_address']

        # Update shipping address
        user.shipping_address.address = shipping_address_data['address']
        user.shipping_address.city = shipping_address_data['city']
        user.shipping_address.postal_code = shipping_address_data['postal_code']
        user.shipping_address.country = shipping_address_data['country']
        user.shipping_address.region = shipping_address_data['region']
        user.shipping_address.save()

        # Create new billing address if addresses are no longer the same
        if not request.data['addresses_are_same']:
            billing_address = Address.objects.create(
                address=billing_address_data['address'],
                city=billing_address_data['city'],
                postal_code=billing_address_data['postal_code'],
                country=billing_address_data['country'],
                region=billing_address_data['region']
            )
            user.billing_address = billing_address
        else:
            user.billing_address = user.shipping_address

        is_supplier = request.data.get('supplier', None)
        if is_supplier:
            supplier_data = request.data['supplier']
            supplier = request.user.supplier
            supplier.keg_deposit_price = supplier_data['keg_deposit_price']
            supplier.default_payment_term = supplier_data['default_payment_term']
            supplier.save()

        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
def get_stripe_token(request, userId):
    """
        Create a verification token on the user and use that for the stripe connect state
    """
    if userId != request.user.id:
        return Response({'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)
    
    user = User.objects.get(pk=userId)
    user.verification_token = token_urlsafe(16)
    user.save()
    return Response({'token': user.verification_token}, status.HTTP_200_OK)
    

@api_view(["POST"])
def create_payment_account(request):
    """
    Complete Stripe payment registration
    """
    token = request.data['token']
    code = request.data['code']
    user = User.objects.get(verification_token=token)
    if user != request.user:
        return Response({'message': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)
    
    existing_account = PaymentAccount.objects.filter(user=user)
    if not existing_account:
        stripe.api_key = settings.STRIPE['CLIENT_SECRET']
        url = settings.STRIPE['TOKEN_URL']
        data = {
            'client_secret': settings.STRIPE['CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code'
        }
        res = requests.post(url, data=data)
        if res.status_code == 200:
            json = res.json()
            account = PaymentAccount(stripe_user_id=json['stripe_user_id'], user=user)
            account.save()
            return Response(status.HTTP_201_CREATED)
        else:
            return Response({'message': 'There was a problem connecting to Stripe'}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'message': 'Payment account already exists'}, status.HTTP_400_BAD_REQUEST)
