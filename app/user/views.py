from rest_framework import generics
from user.serializers import UserSerializer # Import the serializer that creates user API

class CreateUserView(generics.CreateAPIView):
    '''Create a new user in the system'''
    serializer_class = UserSerializer # Class variable that stores the serializer