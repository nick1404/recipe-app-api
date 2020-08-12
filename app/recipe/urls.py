from django.urls import path, include
from rest_framework.routers import DefaultRouter # Automatically generates URLs for the viewset

from recipe import views

router = DefaultRouter()
router.register('tags', views.TagViewSet) # Register the viewset with the router
router.register('ingredients', views.IngredientViewSet) # Register the viewset with the router

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]