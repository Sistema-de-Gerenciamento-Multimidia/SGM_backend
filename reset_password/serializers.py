import re
from rest_framework import serializers
from users.models import CustomUser


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not CustomUser.objects.filter(email__exact=value).exists():
            raise serializers.ValidationError("Não foi encontrado um email de usuário correspondente ao fornecido.")
        return value

class PasswordResetConfirmationSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="New Password"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As senhas fornecidas não correspondem.")
        
        # Validação da complexidade da senha (exemplo)
        password = attrs['new_password']
        if not re.search(r'[A-Z]', password):  # Letra maiúscula
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra maiúscula.")
        if not re.search(r'[a-z]', password):  # Letra minúscula
            raise serializers.ValidationError("A senha deve conter pelo menos uma letra minúscula.")
        if not re.search(r'[0-9]', password):  # Número
            raise serializers.ValidationError("A senha deve conter pelo menos um número.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # Caracter especial
            raise serializers.ValidationError("A senha deve conter pelo menos um caractere especial.")
        if len(password) < 8:
            raise serializers.ValidationError("A senha deve conter pelo menos 8 caracteres")
        
        return attrs
