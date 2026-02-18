from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ User Registration Serializer """

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    # TODO: (Waiting for SQL table) Adjust fields
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'username', 'first_name', 'last_name',
            'role', 'student_id'
        ]
    
    def validate(self, data):
        # TODO: pending — confirm if this logic is needed
        # Check if the passwords match
        # if data['password'] != data['password_confirm']:
        #     raise serializers.ValidationError({
        #         'password': 'Passwords do not match'
        #     })
        
        # Check password strength (call the Model method)
        temp_user = User()
        is_valid, message = temp_user.validate_password_strength(data['password'])
        if not is_valid:
            raise serializers.ValidationError({
                'password': message
            })
                
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Use the create_user method of UserManager
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user

class UserLoginSerializer(serializers.Serializer):
    """User Login Serializer"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        # Find users via email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No account found with this email'
            })
        
        if not user.check_password(password):
            raise serializers.ValidationError({
                'password': 'Incorrect password'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'email': 'This account has been disabled'
            })
        
        data['user'] = user
        return data


class UserLogoutSerializer(serializers.Serializer):
    """User Logout Serializer - 用於 JWT blacklist"""
    
    refresh = serializers.CharField()
    
    def validate(self, data):
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        
        try:
            token = RefreshToken(data['refresh'])
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError({
                'refresh': 'Token is invalid or already expired'
            })
        
        return data