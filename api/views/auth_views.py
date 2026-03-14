"""
Authentication Views
Functions: Registration, Login, Logout, Password Reset, Personal Profile Management
"""

from drf_spectacular.utils import extend_schema

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.conf import settings

from api.serializers.user_serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserLoginSerializer,
    UserLogoutSerializer,
    # PasswordResetRequestSerializer,
    # PasswordResetConfirmSerializer,
)
# from api.permissions.rbac import IsStudent, IsStaff, IsAdmin

# from api.models.user import PasswordResetToken

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    To create a new account, the password must meet security requirements (8+ characters, including uppercase and lowercase letters, numbers, and symbols).

    POST /api/auth/register/
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create a user
        user = serializer.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        # Add user role to the token payload
        refresh['role'] = user.role

        return Response(
            {
                "message": "Registration successful.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    Handle POST request for user login.
    
    Args: HTTP request containing user credentials
        
    Returns: JWT access and refresh tokens with user info
    """
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        password = serializer.validated_data.get("password")

        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT refresh token for the user
        refresh = RefreshToken.for_user(user)
        # Add user role to the token payload
        refresh['role'] = user.role

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(request=None, responses={200: None})
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserLogoutSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# Advanced Feature - required Serializer
# ============================================
# class PasswordResetRequestView(APIView):
#     """
#     Password reset request API (FR-2 Advanced)

#     POST /api/auth/password-reset/
#     {
#         "email": "student@university.edu"
#     }

#     """
#     permission_classes = [AllowAny]
#     serializer_class = PasswordResetRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         email = serializer.validated_data['email']

#         try:
#             user = User.objects.get(email=email, is_active=True)

#             reset_token = get_random_string(64)
#             expires_at = timezone.now() + timezone.timedelta(hours=24)

#             PasswordResetToken.objects.create(
#                 user=user,
#                 token=reset_token,
#                 expires_at=expires_at
#             )

#             # TODO: pending — confirm if this logic is needed - send mail to reset password
#             reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
#             send_mail(
#                 subject='Password Reset Request - Lost & Found System',
#                 message=f'Click this link to reset your password: {reset_link}\nThis link expires in 24 hours.',
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[user.email],
#                 fail_silently=False,
#             )

#             return Response({
#                 'message': 'Password reset email sent. Please check your inbox.'
#             }, status=status.HTTP_200_OK)

#         except User.DoesNotExist:
#             # Security considerations: Do not disclose whether the user exists
#             return Response({
#                 'message': 'If the email exists, a reset link has been sent.'
#             }, status=status.HTTP_200_OK)


# class PasswordResetConfirmView(APIView):
#     """
#     Confirm Password Reset API (FR-2 Advanced)

#     POST /api/auth/password-reset/confirm/
#     {
#         "token": "abc123...",
#         "new_password": "NewSecurePass123!",
#         "new_password_confirm": "NewSecurePass123!"
#     }
#     """
#     permission_classes = [AllowAny]
#     serializer_class = PasswordResetConfirmSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         token = serializer.validated_data['token']
#         new_password = serializer.validated_data['new_password']

#         try:
#             reset_token = PasswordResetToken.objects.get(
#                 token=token,
#                 is_used=False,
#                 expires_at__gt=timezone.now()
#             )

#             user = reset_token.user
#             user.set_password(new_password)
#             user.save()

#             reset_token.is_used = True
#             reset_token.save()

#             return Response({
#                 'message': 'Password has been reset successfully.'
#             }, status=status.HTTP_200_OK)

#         except PasswordResetToken.DoesNotExist:
#             return Response({
#                 'error': 'Invalid or expired token'
#             }, status=status.HTTP_400_BAD_REQUEST)


# class UserProfileView(generics.RetrieveUpdateAPIView):
# """
# User Profile API (Advanced Feature)

# GET /api/auth/profile/
# POST /api/auth/profile/  - update User Profile
# """
# serializer_class = UserProfileSerializer
# permission_classes = [IsAuthenticated]

# def get_object(self):
#     return self.request.user

# def update(self, request, *args, **kwargs):
#     partial = kwargs.pop('partial', False)
#     instance = self.get_object()
#     serializer = self.get_serializer(instance, data=request.data, partial=partial)
#     serializer.is_valid(raise_exception=True)
#     self.perform_update(serializer)

#     return Response({
#         'message': 'Profile updated successfully',
#         'user': serializer.data
#     })
