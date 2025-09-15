from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.users.models import EmailVerification, PasswordReset, UserProfile

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model."""

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "bio": "Test bio",
            "date_of_birth": "1990-01-01",
        }

    def test_create_user(self):
        """Test creating a user with required fields"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password("testpass123"))

    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), "test@example.com")

    def test_user_email_unique(self):
        """Test that email must be unique"""
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="test@example.com", username="anotheruser", password="testpass123"
            )

    def test_user_required_fields(self):
        """Test that email is required"""
        with self.assertRaises(ValueError):
            User.objects.create_user(username="testuser", email="")


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user, role="student", language_preference="en", timezone="UTC"
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, "student")
        self.assertTrue(profile.is_active)

    def test_user_profile_str_representation(self):
        """Test user profile string representation"""
        profile = UserProfile.objects.create(user=self.user, role="teacher")
        self.assertEqual(str(profile), "test@example.com - teacher")

    def test_user_profile_default_values(self):
        """Test user profile default values"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.role, "student")
        self.assertEqual(profile.language_preference, "en")
        self.assertEqual(profile.timezone, "UTC")
        self.assertEqual(profile.notification_preferences, {})


class EmailVerificationModelTest(TestCase):
    """Test cases for EmailVerification model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_create_email_verification(self):
        """Test creating an email verification token"""
        verification = EmailVerification.objects.create(
            user=self.user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        self.assertEqual(verification.user, self.user)
        self.assertEqual(verification.token, "test-token-123")
        self.assertFalse(verification.is_used)

    def test_email_verification_str_representation(self):
        """Test email verification string representation"""
        verification = EmailVerification.objects.create(
            user=self.user,
            token="test-token-123",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        self.assertEqual(str(verification), "Verification for test@example.com")


class PasswordResetModelTest(TestCase):
    """Test cases for PasswordReset model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_create_password_reset(self):
        """Test creating a password reset token"""
        reset = PasswordReset.objects.create(
            user=self.user,
            token="reset-token-123",
            expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertEqual(reset.user, self.user)
        self.assertEqual(reset.token, "reset-token-123")
        self.assertFalse(reset.is_used)

    def test_password_reset_str_representation(self):
        """Test password reset string representation"""
        reset = PasswordReset.objects.create(
            user=self.user,
            token="reset-token-123",
            expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertEqual(str(reset), "Reset for test@example.com")
