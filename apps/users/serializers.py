from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.users.models import User
from apps.users.services import UserService


class UserPublicSerializer(serializers.ModelSerializer):
    """Public user information returned upon registration."""

    class Meta:
        model = User
        fields = ('id', 'username', 'lives')
        read_only_fields = ('id', 'username', 'lives')


class UserProfileSerializer(serializers.ModelSerializer):
    """Full user profile for GET /api/auth/me/ endpoint."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'lives')
        read_only_fields = ('id', 'username', 'email', 'lives')


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for player registration with validation."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='Player password (minimum 6 characters).'
    )
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        default='',
        help_text='Optional player email address.'
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A player with this username already exists.')
        return value

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data.get('email', '')
        user, _ = UserService.create_player(username=username, password=password, email=email)
        return user


class UserRegisterResponseSerializer(serializers.Serializer):
    """Response returned upon successful registration (HTTP 201)."""

    access = serializers.CharField(help_text='JWT Access token.')
    refresh = serializers.CharField(help_text='JWT Refresh token.')
    user = UserPublicSerializer(help_text='Registered player basic details.')


class LoginRequestSerializer(serializers.Serializer):
    """Serializer for player login."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                {'detail': 'Invalid username or password.'}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': 'This account is deactivated.'}
            )

        attrs['user'] = user
        return attrs


class TokenPairResponseSerializer(serializers.Serializer):
    """Response serializer for JWT token pairs."""

    access = serializers.CharField()
    refresh = serializers.CharField()


class UpdateLivesSerializer(serializers.Serializer):
    """Serializer for updating player lives."""

    lives = serializers.IntegerField(
        required=True,
        help_text='New lives count (must be >= 0).'
    )

    def validate_lives(self, value):
        if value < 0:
            raise serializers.ValidationError('Lives count cannot be negative.')
        return value


class UpdateLivesResponseSerializer(serializers.Serializer):
    """Response serializer after lives update."""

    lives = serializers.IntegerField()
