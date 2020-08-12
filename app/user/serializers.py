from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _ # For other languages?
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    '''Serializer for users object'''
    
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}
        
    def create(self, validated_data):
        """Create a new user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        """Update an existing user, setting password correctly"""
        password = validated_data.pop('password', None) # POP removes password from dictionary after retrieving
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
            
        return user
    
    
class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication token"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False        
    )
    
    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Invalid credentials')
            raise serializers.ValidationError(msg, code='authentication')
        
        attrs['user'] = user
        return attrs # Must return attrs when overriding "validate" function