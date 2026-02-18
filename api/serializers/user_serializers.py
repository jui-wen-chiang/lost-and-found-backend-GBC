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