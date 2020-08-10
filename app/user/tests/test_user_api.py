from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Rest Framework Imports
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

def create_user(**params):
    '''Helper function for user creation'''
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    '''Test the users API (public)'''
    
    def setUp(self):
        self.client = APIClient()
        
    def test_create_valid_user(self):
        '''Test creating user with valid payload is successful'''
        payload = {
            'email': 'test@example.com',
            'password': 'password',
            'name': 'xxx'
        }
        
        # Make a post request to create a user
        response = self.client.post(CREATE_USER_URL, payload)
        
        # Checl that request is successful
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        
        # Check that password is not returned in the response
        self.assertNotIn('password', response.data)
        
        
    def test_user_exists(self):
        '''Test creating a user that already exists fails'''
        payload = {
            'email': 'test@example.com',
            'password': 'password',
            'name': 'xxx'
        }
        create_user(**payload)
        
        response = self.client.post(CREATE_USER_URL, payload)
        
        # Check that the response is "Bad Request" as the user already exists
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_password_too_short(self):
        '''Test that the password is more than 5 characters'''
        payload = {
            'email': 'test@example.com',
            'password': 'pw'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        
        # Check the response is HTTP_400_BAD_REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check the user was never created
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        
        self.assertFalse(user_exists)
        