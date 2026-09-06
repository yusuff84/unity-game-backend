from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.models import User
from apps.users.services import UserService


class UserServiceTests(TestCase):
    """Unit tests for UserService business logic layer."""

    def test_create_player_success(self):
        user, tokens = UserService.create_player(
            username='gamer1',
            password='secretpassword',
            email='gamer1@game.local'
        )
        self.assertEqual(user.username, 'gamer1')
        self.assertEqual(user.lives, 5)
        self.assertEqual(user.email, 'gamer1@game.local')
        self.assertTrue(user.check_password('secretpassword'))
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)

    def test_generate_tokens_for_user(self):
        user = User.objects.create_user(username='gamer2', password='password123')
        tokens = UserService.generate_tokens_for_user(user)
        self.assertIn('access', tokens)
        self.assertIn('refresh', tokens)
        self.assertIsInstance(tokens['access'], str)
        self.assertIsInstance(tokens['refresh'], str)

    def test_update_player_lives_success(self):
        user = User.objects.create_user(username='gamer3', password='password123')
        lives = UserService.update_player_lives(user, 2)
        self.assertEqual(lives, 2)
        user.refresh_from_db()
        self.assertEqual(user.lives, 2)

    def test_update_player_lives_negative_raises_error(self):
        user = User.objects.create_user(username='gamer4', password='password123')
        with self.assertRaises(ValidationError):
            UserService.update_player_lives(user, -5)
