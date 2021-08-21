from rest_framework import serializers
from .models import User, FileManager
from django.contrib.auth import authenticate

from rest_framework import exceptions


class ProfileSerializer(serializers.ModelSerializer):
    """
        Creates a new user.
        Email, username, and password are required.
        Returns a JSON web token.
    """

    # The password must be validated and should not be read by the client
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password', 'phone')

    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        instance.set_auth()

        return instance


class LoginSerializer(serializers.Serializer):
    """
    Authenticates an existing user.
    Email and password are required.
    Returns a JSON web token.
    """
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        """
        Validates user data.
        """
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise exceptions.AuthenticationFailed()

        user = authenticate(username=email, password=password)

        if user is None:
            raise exceptions.AuthenticationFailed()

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return user.get_data()


class FileManagerSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileManager
        fields = ('id', 'profile', 'video')
