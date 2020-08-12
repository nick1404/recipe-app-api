from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import UserSerializer, AuthTokenSerializer # Import the serializers that create user API

class CreateUserView(generics.CreateAPIView):
    '''Create a new user in the system'''
    serializer_class = UserSerializer # Class variable that stores the serializer
    
class CreateTokenView(ObtainAuthToken):
    """Create a new token from user credentials"""
    serializer_class = AuthTokenSerializer 
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES # Allows to render in the browser
    
    
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_object(self):
        """Retrieve and return authenticated classes"""
        return self.request.user