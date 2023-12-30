from django.test import TestCase

# Create your tests here.
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserLoginViewTestCase(APITestCase):

    def setUp(self):
        # Create a user for testing
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.login_url = reverse('user-login')
        self.token = Token.objects.create(user=self.user)


    # user login tests
    def test_user_login_successful(self):
        # Test a successful login
        data = {'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['response'])
        self.assertIn('user_id', response.data['response'])

    def test_user_login_unsuccessful(self):
        # Test an unsuccessful login with invalid credentials
        data = {'email': 'test@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid email or password')


    # user logout tests
    def test_user_logout_successful(self):
        # Authenticate the user with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Test a successful logout
        logout_url = reverse('user-logout')
        response = self.client.post(logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the token has been deleted
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(key=self.token.key)



    # user details tests
    def test_get_user_details(self):
        # Authenticate the user with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Test the GET method for user details
        user_detail_url = reverse('user-details', args=[self.user.id])
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.user.id)

    def test_get_user_details_unauthenticated(self):
        # Test the GET method for user details when the user is not authenticated
        user_detail_url = reverse('user-details', args=[self.user.id])
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_user_details(self):
        # Authenticate the user with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        # Test the PATCH method for updating user details
        user_detail_url = reverse('user-details', args=[self.user.id])
        data = {'email': 'updated@example.com'}
        response = self.client.patch(user_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['result'], "User's details updated!")

        # Verify that the user details have been updated in the database
        updated_user = get_user_model().objects.get(id=self.user.id)
        self.assertEqual(updated_user.email, 'updated@example.com')

    def test_patch_user_details_unauthenticated(self):
        # Test the PATCH method for updating user details when the user is not authenticated
        user_detail_url = reverse('user-details', args=[self.user.id])
        data = {'email': 'updated@example.com'}
        response = self.client.patch(user_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
