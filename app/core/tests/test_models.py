from django.contrib.auth import get_user_model
from django.test import TestCase
from core import models
from unittest.mock import patch

def sample_user(email='admin@example.com', password='testpass'):
    """Create a new sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    
    def test_create_user_with_email(self):
        '''Test creating a new user with email is successful'''
        email = 'nick1404@lancaster.ac.uk'
        password = '1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
    def test_new_user_email_lowercase(self):
        '''Test user's email is all lowercased'''
        email = 'nick@LANCASTER.AC.UK'
        user = get_user_model().objects.create_user(email, '1234')
        
        self.assertEqual(user.email, email.lower())
        
    def test_new_user_invalid_email(self):
        '''Test that creating user with no email raises error'''
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '1234')
            
    def test_super_user_created(self):
        '''Test creating a new superuser'''
        user = get_user_model().objects.create_superuser(
            'nick@lancs.ac.uk',
            '1234'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(), name='Vegan'
        )
        
        self.assertEqual(str(tag), tag.name) # Check that the tag name is a string
        
    def test_ingredients_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(), name='Cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)
        
    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(), title = 'Egg fried rice',
            time_minutes=5, price=5.00
        )
    
    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        
        exp_path = f'uploads/recipe/{uuid}.jpg' # Same as .format()
        self.assertEqual(file_path, exp_path)   