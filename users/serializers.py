from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'avatar', ]
        extra_kwargs = {'password': {'write_only': True}}  # Don't return password in response
        read_only_fields = ('id',)  # Ensure the ID is read-only

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),  # Handle optional name field
            last_name=validated_data.get('last_name', ''),  # Handle optional name field
            avatar=validated_data.get('avatar', ''),  # Handle optional bio field
        )
        user.set_password(validated_data['password'])  # Set password securely
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
