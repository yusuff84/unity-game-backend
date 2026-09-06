"""
Business logic and application services for User management.
Follows Clean Architecture principles by isolating domain logic from framework views.
"""

from typing import Dict, Tuple
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class UserService:
    """Service handling player account operations and token generation."""

    @staticmethod
    def create_player(username: str, password: str, email: str = '') -> Tuple[User, Dict[str, str]]:
        """
        Creates a new player with default 5 lives and hashed password.
        Returns the created user and JWT tokens (access, refresh).
        """
        user = User(
            username=username,
            email=email.strip().lower() if email else '',
            lives=5  # Requirement: Upon registration lives = 5
        )
        user.set_password(password)
        user.full_clean()
        user.save()

        tokens = UserService.generate_tokens_for_user(user)
        return user, tokens

    @staticmethod
    def generate_tokens_for_user(user: User) -> Dict[str, str]:
        """Generates JWT access and refresh tokens for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

    @staticmethod
    def update_player_lives(user: User, lives: int) -> int:
        """
        Updates player lives.
        Enforces validation: lives must not be negative (< 0).
        """
        if lives < 0:
            raise ValidationError({'lives': 'Lives count cannot be negative.'})

        return user.update_lives(lives)
