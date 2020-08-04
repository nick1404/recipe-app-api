from django.contrib.auth import get_user_model
from django.test import TestCase

class ModelTests(TestCase):
    
    def test_create_user_with_email(self):
        '''Test creating a new user with email is successful'''
        email = 'nick1404@lancaster.ac.uk'
        password = '1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        
        self.assertEqual(user.email(), email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_lowercase(self):
        '''Test user's email is all lowercased'''
        email = 'nick@LANCASTER.AC.UK'
        user = get_user_model().objects.create_user(email, '1234')
        
        self.assertEqual(user.email(), email.lower())