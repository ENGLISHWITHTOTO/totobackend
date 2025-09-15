from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerification, PasswordReset
import uuid
from datetime import datetime, timedelta


def send_verification_email(user):
    """Send email verification token"""
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=24)

    EmailVerification.objects.create(user=user, token=token, expires_at=expires_at)

    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    send_mail(
        "Verify Your Email - English with Toto",
        f"Please click the link to verify your email: {verification_url}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user):
    """Send password reset token"""
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(hours=1)

    PasswordReset.objects.create(user=user, token=token, expires_at=expires_at)

    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    send_mail(
        "Password Reset - English with Toto",
        f"Please click the link to reset your password: {reset_url}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
