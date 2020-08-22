from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

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
        
    def test_create_ingredient_successful(self):
        """Test creating an ingredient"""
        payload = {'name': 'cabbage'}
        self.client.post(INGREDIENTS_URL, payload)
        
        # Check that the ingredient has been created
        exists = Ingredient.objects.filter(user=self.user, name=payload['name']).exists()
        self.assertTrue(exists)
        
    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {'name': ''}
        response = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            name='Cucumber', user=self.user
        )
        ingredient2 = Ingredient.objects.create(
            name='Tomato', user=self.user
        )
        recipe = Recipe.objects.create(
            title='Salad',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)
        
        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)
        
    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(
            name='Eggs', user=self.user
        )
        Ingredient.objects.create(user=self.user, name='Cheese')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=5,
            price=5.00,
            user=self.user,
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='Boiled Egg',
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)
        
        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(response.data), 1)