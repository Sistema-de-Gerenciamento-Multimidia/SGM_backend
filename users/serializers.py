from rest_framework import serializers  
from users.models import User


class UserRegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        max_length=16,
        style={'input_type': 'password'}
    )
    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'name', 'password', 'password_confirmation')

    def validate(self, data):
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')

        if password != password_confirmation:
            raise serializers.ValidationError({'password_confirmation': "Passwords do not match."})
        
        return data
    

class UserListDetailSerializer(serializers.ModelSerializer):

    class Meta():
        model = User
        fields = ['email', 'username', 'name', 'description']