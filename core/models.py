from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class Role(models.TextChoices):
    """User roles for the platform."""

    ADMIN = "ADMIN", "Admin"
    INSTRUCTOR = "INSTRUCTOR", "Instructor"
    STUDENT = "STUDENT", "Student"


class UserManager(BaseUserManager):
    """Custom user manager for handling user creation."""

    def create_user(self, email, password=None, role=Role.STUDENT, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, role=Role.ADMIN, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with role-based authentication."""

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.email} ({self.role})"


class TimeStampedModel(models.Model):
    """Abstract base class with self-updating created and modified fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Location(models.Model):
    """Location model for addresses and geographical data."""

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        db_table = "core_location"


class FileAttachment(TimeStampedModel):
    """File attachment model for user uploads."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="attachments/%Y/%m/")
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()

    class Meta:
        db_table = "core_file_attachment"


class Conversation(TimeStampedModel):
    """Conversation model for messaging between users."""

    participants = models.ManyToManyField(User, related_name="conversations")
    title = models.CharField(max_length=200, blank=True)
    last_message_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversation"
        ordering = ["-last_message_at"]


class Message(TimeStampedModel):
    """Message model for conversation messages."""

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "message"
        ordering = ["created_at"]


class Booking(TimeStampedModel):
    """Booking model for lesson and homestay bookings."""

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    )

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings_as_student"
    )
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings_as_instructor"
    )
    homestay = models.ForeignKey(
        "homestay.Homestay", on_delete=models.CASCADE, null=True, blank=True
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "booking"


class TimeSlot(TimeStampedModel):
    """Time slot model for instructor availability."""

    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="time_slots"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    recurring = models.BooleanField(default=False)

    class Meta:
        db_table = "time_slot"


class Notification(TimeStampedModel):
    """Notification model for user notifications."""

    TYPE_CHOICES = (
        ("message", "New Message"),
        ("booking", "Booking Update"),
        ("payment", "Payment"),
        ("system", "System"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_content_type = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]


class NotificationPreference(TimeStampedModel):
    """Notification preferences model for user settings."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    email_messages = models.BooleanField(default=True)
    email_bookings = models.BooleanField(default=True)
    email_payments = models.BooleanField(default=True)
    push_messages = models.BooleanField(default=True)
    push_bookings = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_preference"
