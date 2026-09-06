from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.serializers import (
    LoginRequestSerializer,
    TokenPairResponseSerializer,
    UpdateLivesResponseSerializer,
    UpdateLivesSerializer,
    UserProfileSerializer,
    UserRegisterResponseSerializer,
    UserRegisterSerializer,
)
from apps.users.services import UserService


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new player with default 5 lives.
    Generates and returns JWT tokens along with player details.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserRegisterSerializer,
        responses={
            201: OpenApiResponse(response=UserRegisterResponseSerializer, description="Player registered successfully"),
            400: OpenApiResponse(description="Validation error (e.g. username taken or missing fields)"),
        },
        description="Register a new player account. Automatically assigns 5 lives and returns JWT credentials.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = UserService.generate_tokens_for_user(user)

        response_data = {
            'access': tokens['access'],
            'refresh': tokens['refresh'],
            'user': {
                'id': user.id,
                'username': user.username,
                'lives': user.lives,
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates a player using username and password.
    Returns access and refresh JWT tokens.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginRequestSerializer,
        responses={
            200: OpenApiResponse(response=TokenPairResponseSerializer, description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials or inactive account"),
        },
        description="Authenticate player credentials and return JWT token pair.",
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        tokens = UserService.generate_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):
    """
    POST /api/auth/token/refresh/
    Exchanges a valid refresh token for a fresh access token.
    """
    @extend_schema(
        description="Refresh JWT access token using a valid refresh token.",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(APIView):
    """
    GET /api/auth/me/
    Retrieves the authenticated player's personal profile and lives.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(response=UserProfileSerializer, description="Current player profile data"),
            401: OpenApiResponse(description="Unauthorized - Token invalid or missing"),
        },
        description="Fetch information about the currently authenticated player.",
        tags=["Player Profile"],
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateLivesView(APIView):
    """
    PATCH /api/auth/me/lives/
    Updates the authenticated player's lives count.
    Lives cannot be negative (< 0).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UpdateLivesSerializer,
        responses={
            200: OpenApiResponse(response=UpdateLivesResponseSerializer, description="Lives updated successfully"),
            400: OpenApiResponse(description="Validation error (e.g. lives < 0 or invalid data)"),
            401: OpenApiResponse(description="Unauthorized - Token invalid or missing"),
        },
        description="Update player's remaining lives. Validates that lives cannot be negative.",
        tags=["Player Profile"],
    )
    def patch(self, request):
        serializer = UpdateLivesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_lives = serializer.validated_data['lives']

        try:
            UserService.update_player_lives(request.user, new_lives)
        except DjangoValidationError as exc:
            return Response(
                exc.message_dict if hasattr(exc, 'message_dict') else {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'lives': new_lives}, status=status.HTTP_200_OK)
