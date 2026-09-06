from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.users.admin import UserAdmin

User = get_user_model()


class MockRequest:
    pass


class MockMessageMiddleware:
    def __init__(self):
        self.messages = []

    def add(self, level, message, extra_tags=''):
        self.messages.append(message)


class UserAdminTests(TestCase):
    """Unit tests for Custom UserAdmin interface and actions."""

    def setUp(self):
        self.site = AdminSite()
        self.admin = UserAdmin(User, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='adminplayer', password='password123', lives=3)

    def test_email_display(self):
        self.assertIn('—', self.admin.email_display(self.user))
        self.user.email = 'admin@game.local'
        self.user.save()
        self.assertEqual(self.admin.email_display(self.user), 'admin@game.local')

    def test_lives_badge(self):
        badge_html = self.admin.lives_badge(self.user)
        self.assertIn('3', badge_html)

    def test_action_reset_lives_to_default(self):
        request = self.factory.get('/admin/')
        request._messages = MockMessageMiddleware()

        queryset = User.objects.filter(id=self.user.id)
        self.admin.action_reset_lives_to_default(request, queryset)

        self.user.refresh_from_db()
        self.assertEqual(self.user.lives, 5)

    def test_action_add_one_life(self):
        request = self.factory.get('/admin/')
        request._messages = MockMessageMiddleware()

        queryset = User.objects.filter(id=self.user.id)
        self.admin.action_add_one_life(request, queryset)

        self.user.refresh_from_db()
        self.assertEqual(self.user.lives, 4)

    def test_action_set_lives_to_zero(self):
        request = self.factory.get('/admin/')
        request._messages = MockMessageMiddleware()

        queryset = User.objects.filter(id=self.user.id)
        self.admin.action_set_lives_to_zero(request, queryset)

        self.user.refresh_from_db()
        self.assertEqual(self.user.lives, 0)

    def test_password_action_button(self):
        btn_html = self.admin.password_action_button(self.user)
        self.assertIn('Сменить пароль', btn_html)
        self.assertIn(f'/admin/users/user/{self.user.id}/password/', btn_html)

    def test_change_password_action_redirect(self):
        request = self.factory.get(f'/admin/users/user/{self.user.id}/change_password_action/')
        response = self.admin.change_password_action(request, self.user.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/admin/users/user/{self.user.id}/password/')
