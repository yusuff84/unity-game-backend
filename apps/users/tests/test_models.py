from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.users.models import User


class UserModelTests(TestCase):
    """Unit tests for the custom User model."""

    def test_user_creation_with_default_lives(self):
        """Ensure a newly created user has default 5 lives and properly hashed password."""
        user = User.objects.create_user(
            username='player123',
            password='securepassword123'
        )
        self.assertEqual(user.username, 'player123')
        self.assertEqual(user.lives, 5)
        self.assertEqual(user.email, '')
        self.assertTrue(user.check_password('securepassword123'))
        self.assertFalse(user.password == 'securepassword123')
        self.assertIsNotNone(user.created_at)

    def test_user_negative_lives_validation_on_clean(self):
        """Ensure clean() raises ValidationError if lives < 0."""
        user = User(username='test_negative', lives=-1)
        with self.assertRaises(ValidationError):
            user.clean()

    def test_user_negative_lives_validation_on_save(self):
        """Ensure save() raises ValidationError if lives < 0."""
        user = User(username='test_negative', lives=-1)
        user.set_password('pass1234')
        with self.assertRaises(ValidationError):
            user.save()

    def test_update_lives_domain_method(self):
        """Test domain helper method update_lives."""
        user = User.objects.create_user(username='player', password='password123')
        updated = user.update_lives(3)
        self.assertEqual(updated, 3)
        user.refresh_from_db()
        self.assertEqual(user.lives, 3)

        with self.assertRaises(ValidationError):
            user.update_lives(-1)

    def test_string_representation(self):
        user = User.objects.create_user(username='hero', password='password123')
        self.assertIn('hero', str(user))
        self.assertIn('5', str(user))
