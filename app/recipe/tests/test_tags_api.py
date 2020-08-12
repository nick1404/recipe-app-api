from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsAPITests(TestCase):
    """Test the publicly available tags API"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_login_required(self):
        """Test login is required for retrieving tags"""
        response = self.client.get(TAGS_URL)
        
        # Check that the request is unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateTagsAPITests(TestCase):
    """Test the authorized user tags API."""
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com', 'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        
    def test_retrieve_tags(self):
        """Test retrieving tags"""
        
        # Create two sample tags
        Tag.objects.create(user=self.user,name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        
        response = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True) # Serialize all tags, not just the first one
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'otherUser@example.com', 'password'
        )
        Tag.objects.create(user=user2, name='Fruity') # Create other user
        
        tag = Tag.objects.create(user=self.user, name='SOmeFood') # Create tag wiht authenticated user
        
        response = self.client.get(TAGS_URL)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # Check that a single tag is returned
        self.assertEqual(response.data[0]['name'], tag.name) # Compare that names of tags are the same
        
    def test_create_tag_successful(self):
        """Tests that a tag is created successfully"""
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, payload)
        
        # Check that the tag exists
        exists = Tag.objects.filter(
            user=self.user, name=payload['name']
        ).exists() # True if the tag exists
        
        self.assertTrue(exists)
        
    def test_create_invalid_tag(self):
        """Test creating a tag with an invalid payload"""
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)