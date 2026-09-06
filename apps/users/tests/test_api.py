from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class AuthAPITests(APITestCase):
    """Integration tests for Authentication endpoints."""

    def setUp(self):
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.refresh_url = reverse('token-refresh')
        self.me_url = reverse('user-me')
        self.lives_url = reverse('user-me-lives')

    def test_register_success(self):
        """
        Test POST /api/auth/register/
        Expected:
        HTTP 201 Created
        {"access": "...", "refresh": "...", "user": {"id": 1, "username": "player123", "lives": 5}}
        """
        payload = {
            "username": "player123",
            "password": "password123"
        }
        response = self.client.post(self.register_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'player123')
        self.assertEqual(user_data['lives'], 5)
        self.assertIsInstance(user_data['id'], int)

        # Verify DB state
        user = User.objects.get(username='player123')
        self.assertEqual(user.lives, 5)
        self.assertTrue(user.check_password('password123'))

    def test_register_duplicate_username_fails(self):
        User.objects.create_user(username='player123', password='password123')

        payload = {
            "username": "player123",
            "password": "password456"
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_register_with_optional_email(self):
        payload = {
            "username": "emailplayer",
            "password": "password123",
            "email": "test@unitygame.io"
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='emailplayer')
        self.assertEqual(user.email, 'test@unitygame.io')

    def test_login_success(self):
        """
        Test POST /api/auth/login/
        Expected:
        HTTP 200 OK
        {"access": "...", "refresh": "..."}
        """
        User.objects.create_user(username='player123', password='password123')

        payload = {
            "username": "player123",
            "password": "password123"
        }
        response = self.client.post(self.login_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        User.objects.create_user(username='player123', password='password123')

        payload = {
            "username": "player123",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

    def test_token_refresh_success(self):
        """
        Test POST /api/auth/token/refresh/
        Expected:
        HTTP 200 OK
        {"access": "..."}
        """
        user = User.objects.create_user(username='player123', password='password123')
        refresh = RefreshToken.for_user(user)

        payload = {
            "refresh": str(refresh)
        }
        response = self.client.post(self.refresh_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_invalid(self):
        payload = {
            "refresh": "invalid.jwt.token"
        }
        response = self.client.post(self.refresh_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_me_authenticated(self):
        """
        Test GET /api/auth/me/
        Expected:
        HTTP 200 OK
        {"id": 1, "username": "player123", "email": "", "lives": 5}
        """
        user = User.objects.create_user(username='player123', password='password123', email='player@game.io')
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['username'], 'player123')
        self.assertEqual(response.data['email'], 'player@game.io')
        self.assertEqual(response.data['lives'], 5)

    def test_get_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_lives_success(self):
        """
        Test PATCH /api/auth/me/lives/
        Expected:
        HTTP 200 OK
        {"lives": 4}
        """
        user = User.objects.create_user(username='player123', password='password123')
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        payload = {"lives": 4}
        response = self.client.patch(self.lives_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"lives": 4})

        user.refresh_from_db()
        self.assertEqual(user.lives, 4)

    def test_patch_lives_to_zero_allowed(self):
        """Player can have 0 lives (game over state)."""
        user = User.objects.create_user(username='player123', password='password123')
        refresh = RefreshToken.for_user(user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.patch(self.lives_url, {"lives": 0}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"lives": 0})
        user.refresh_from_db()
        self.assertEqual(user.lives, 0)

    def test_patch_lives_negative_rejected(self):
        """
        Requirement: "Не разрешать lives < 0."
        Expected:
        HTTP 400 Bad Request
        """
        user = User.objects.create_user(username='player123', password='password123')
        refresh = RefreshToken.for_user(user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        payload = {"lives": -1}
        response = self.client.patch(self.lives_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertEqual(user.lives, 5)  # Should remain unchanged

    def test_patch_lives_unauthenticated(self):
        payload = {"lives": 4}
        response = self.client.patch(self.lives_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_lives_invalid_format(self):
        user = User.objects.create_user(username='player123', password='password123')
        refresh = RefreshToken.for_user(user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        payload = {"lives": "invalid_number"}
        response = self.client.patch(self.lives_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
