from django.urls import path

from apps.users.views import (
    CustomTokenRefreshView,
    LoginView,
    RegisterView,
    UpdateLivesView,
    UserProfileView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('me/', UserProfileView.as_view(), name='user-me'),
    path('me/lives/', UpdateLivesView.as_view(), name='user-me-lives'),
]
