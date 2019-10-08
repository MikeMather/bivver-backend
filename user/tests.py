from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from.models import *
import json


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='bivver', verified=True)
        self.user.set_password('secret')
        self.user.save()

    # def test_can_create_user(self):
    #     response = self.client.post('/user/users/', {'username': 'vinocount', 'password': 'secret', "groups": []})
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertIsNotNone(get_user_model().objects.get(username='vinocount'))

    def test_can_login(self):
        url = '/auth/token/'
        response = self.client.post(url, {'username': 'bivver', 'password': 'secret'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), ['refresh', 'access'])
    
    def test_fail_login_on_incorrect_credentials(self):
        url = '/auth/token/'
        response = self.client.post(url, {'username': 'bivver', 'password': 'nottheactualpassword'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'No active account found with the given credentials')
