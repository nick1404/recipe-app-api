from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsAPITests(TestCase):
    """Tests the publicly available ingredients API"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_login_required(self):
        """Tests the login is required to access the endpoint"""
        response = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateIngredientsAPITests(TestCase):
    """Test the private ingredients API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com', 'testpass'
        )
        self.client.force_authenticate(self.user)
        
    def test_retrieve_ingredients_list(self):
        """Test retrieving a list of ingredients"""
        
        # Create two new ingredients
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        
        response = self.client.get(INGREDIENTS_URL)
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
    def test_ingredients_limited_to_user(self):
        """Test that ingredients are limited to the authenticated user."""
        
        # Create another user with an ingredient
        user2 = get_user_model().objects.create_user(
            'otherUser@example.com', 'otherpass'
        )
        Ingredient.objects.create(user=user2, name='Shite')
        
        # Create an ingredient with the authenticated user
        ingredient = Ingredient.objects.create(user=self.user, name='Fries')
        
        response = self.client.get(INGREDIENTS_URL)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)