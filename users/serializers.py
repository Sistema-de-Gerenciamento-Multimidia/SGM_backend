from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser


class CustomUserUpdateListDetailSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateTimeField(
        required=False,
        format="%d/%m/%Y",
        input_formats=["%d/%m/%Y", "%d-%m-%Y"]
    )

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'name', 'description', 
            'profile_picture', 'date_of_birth',
        ]
        read_only_fields = ['id']

class CustomUserCreateSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateTimeField(
        required=False,
        format="%d/%m/%Y",
        input_formats=["%d/%m/%Y", "%d-%m-%Y"]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label="Password"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'name', 'password', 'confirm_password', 'description', 
            'profile_picture', 'date_of_birth',
        ]
        read_only_fields = ['id']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'detail': 'As senhas fornecidas não correspondem.'})
        validate_password(attrs['password'])
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangeUserPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='Current Password'
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='New Password'
    )
    confirm_new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='Confirm New Password'
    )
    
    def validate(self, attrs):
        user = self.context['user']
        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        
        if not user.check_password(current_password):
            raise serializers.ValidationError({'detail': 'Senha atual fornecida está incorreta.'})
        
        if new_password != confirm_new_password:
            raise serializers.ValidationError({'detail': 'As novas senhas fornecidas não correspondem.'})
        
        validate_password(new_password, user)
        
        return attrs
    
    def update(self, instance, validated_data):
        new_password = validated_data['new_password']
        
        instance.set_password(new_password)
        instance.save()
        
        return instance