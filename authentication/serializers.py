from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    data = serializers.IntegerField(read_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user_id'] = self.user.id
        
        return data
