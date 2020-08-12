from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Rest Framework Imports
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token') # URL to be used in POST request to generate token
ME_URL = reverse('user:me')

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
            'name': 'xxx',
        }
        create_user(**payload)
        
        response = self.client.post(CREATE_USER_URL, payload)
        
        # Check that the response is "Bad Request" as the user already exists
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_password_too_short(self):
        '''Test that the password is more than 5 characters'''
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test',
        }
        response = self.client.post(CREATE_USER_URL, payload)
        
        # Check the response is HTTP_400_BAD_REQUEST
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check the user was never created
        user_exists = get_user_model().objects.filter(
            email=payload['email']).exists()
        
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self):
        '''Test that a token is created for a user'''
        payload = {'email': 'test@example.com', 'password': 'testpass'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        
        # Check that the token is in the response
        self.assertIn('token', response.data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_token_invalid_credentials(self):
        """Tests that token is not created if invalid credentials are provided"""
        create_user(email='test@example.com', password='test')
        
        # Give payload with incorrect password
        payload = {'email':'test@example.com', 'password':'wrong'}
        response = self.client.post(TOKEN_URL, payload)
        
        # Check that the token is not in the response and HTTP_400_BAD_REQUEST
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_no_user(self):
        """Test token is not created if user does not exist"""
        payload = {'email': 'test@example.com', 'password': 'testpass'}
        response = self.client.post(TOKEN_URL, payload) 
         
        # Check that the token is not in the response and HTTP_400_BAD_REQUEST
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_create_token_missing_field(self):
        """Test that email and password are required"""
        response = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        
        # Check that the token is not in the response and HTTP_400_BAD_REQUEST
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        response = self.client.get(ME_URL)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateUserAPITest(TestCase):
    """Test API requests that require authentication"""
    
    def setUp(self):
        self.user = create_user(
            email='user@example.com',
            password='password',
            name='test'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)
        
        # Check that connection is established
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })
        
    def test_post_not_allowed(self):
        """Test that POST request is not allowed"""
        response = self.client.post(ME_URL, {})
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
    def test_update_user_profile(self):
        """Test updating user profile for logged in user"""
        payload = {'name': 'newname', 'password': 'newpass'}
        
        response = self.client.patch(ME_URL, payload)
        
        self.user.refresh_from_db() # Update user profile with latest data from DB
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)