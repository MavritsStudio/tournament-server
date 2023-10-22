from rest_framework import serializers
from django.contrib.auth import get_user_model

from account.models import Team


class SignupSerializer(serializers.ModelSerializer):
    """Signup functionality serializer.
    
    Middle name field is optional.
    """

    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    middle_name = serializers.CharField(
        max_length=150, default='', required=False,
    )


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('uid', 'email', 'first_name', 'middle_name', 'last_name')
        read_only_fields = ('uid', 'email')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('code', 'name', 'description', 'mate1', 'mate2', 'created')
        read_only_fields = ('code', )


class TeamWithMatesSerializer(TeamSerializer):
    mate1 = UserSerializer(read_only=True)
    mate2 = UserSerializer(read_only=True)

    class Meta(TeamSerializer.Meta):
        pass
