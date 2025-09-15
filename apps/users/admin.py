from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmailVerification, PasswordReset, User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""

    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_verified",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_verified", "is_staff", "is_active", "created_at")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = list(BaseUserAdmin.fieldsets) + [
        (
            "Additional Info",
            {"fields": ("phone", "avatar", "date_of_birth", "bio", "is_verified")},
        ),
    ]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model."""

    list_display = ("user", "role", "language_preference", "timezone", "is_active")
    list_filter = ("role", "language_preference", "is_active", "created_at")
    search_fields = ("user__email", "user__username")


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    """Admin configuration for EmailVerification model."""

    list_display = ("user", "token", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "token")


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    """Admin configuration for PasswordReset model."""

    list_display = ("user", "token", "created_at", "expires_at", "is_used")
    list_filter = ("is_used", "created_at")
    search_fields = ("user__email", "token")
