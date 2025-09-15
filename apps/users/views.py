from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, EmailVerification, PasswordReset
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .utils import send_verification_email, send_password_reset_email
import uuid
from datetime import datetime, timedelta


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Create user profile
        UserProfile.objects.create(
            user=user, role=serializer.validated_data.get("role", "student")
        )

        # Send verification email
        send_verification_email(user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully. Please check your email for verification.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "is_verified": user.is_verified,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(username=email, password=password)
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "is_verified": user.is_verified,
                        "role": user.profile.role,
                    },
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email(request):
    """Email verification endpoint"""
    token = request.data.get("token")

    try:
        verification = EmailVerification.objects.get(
            token=token, is_used=False, expires_at__gt=datetime.now()
        )

        verification.user.is_verified = True
        verification.user.save()

        verification.is_used = True
        verification.save()

        return Response(
            {"message": "Email verified successfully"}, status=status.HTTP_200_OK
        )

    except EmailVerification.DoesNotExist:
        return Response(
            {"error": "Invalid or expired verification token"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """Password reset request endpoint"""
    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
        send_password_reset_email(user)

        return Response(
            {"message": "Password reset email sent"}, status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    """Password reset confirmation endpoint"""
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    try:
        reset = PasswordReset.objects.get(
            token=token, is_used=False, expires_at__gt=datetime.now()
        )

        # Validate password
        try:
            validate_password(new_password, reset.user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Update password
        reset.user.set_password(new_password)
        reset.user.save()

        reset.is_used = True
        reset.save()

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )

    except PasswordReset.DoesNotExist:
        return Response(
            {"error": "Invalid or expired reset token"},
            status=status.HTTP_400_BAD_REQUEST,
        )
