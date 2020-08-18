from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])
        

def sample_tag(user, name='Main Course'):
    """Create and return a sample tag."""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient."""
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params) # Update defaults with given params
    
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated recipe API access"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_required(self):
        """Test that authentication is required"""
        response = self.client.get(RECIPES_URL)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class PrivateRecipeAPITests(TestCase):
    """Test authenticated recipe API access"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        
        # Create two sample recipes
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        
        response = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
    def test_recipes_limited_to_user(self):
        """Test retrieving a limited-to-user recipe list"""
        user2 = get_user_model().objects.create_user(
            'other@example.com', 'otherpass'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        
        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        
        serializer = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data, serializer.data)
        
    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        
        url = detail_url(recipe.id)
        
        response = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)
        
    def test_create_basic_recipe(self):
        """Tests basic recipe creation"""
        payload = {'title': 'Cheesecake', 'time_minutes': 30, 'price': 5.00}
        response = self.client.post(RECIPES_URL, payload)
        
        # Check that the object was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
    
    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado toast',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        response = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        
        # Since we created two tags, we expect two tags to be returned
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        
    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }
        response = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        
    def test_partial_update_recipe(self):
        """Test updating recipe with PATCH."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        
        payload = {'title': 'Chicken Tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)
        
    def test_full_update_recipe(self):
        """Test updating a recipe with PUT"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')
        
        payload = {'title': 'Spaghetti Carbonara', 
                   'time_minutes': 25,
                   'price': 5.00
                   }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        
        # Check that the tag count is 0
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)