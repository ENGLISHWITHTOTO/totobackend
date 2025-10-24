from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User,
    Location,
    FileAttachment,
    Conversation,
    Message,
    Booking,
    TimeSlot,
    Notification,
    NotificationPreference,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "role",
            "avatar",
            "phone",
            "bio",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "name", "password", "role"]

    def create(self, validated_data):
        """Create a new user with the provided data."""
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """Validate login credentials."""
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid credentials")
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            data["user"] = user
            return data
        raise serializers.ValidationError("Must include email and password")


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for location data."""

    class Meta:
        model = Location
        fields = "__all__"


class FileAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for file attachments."""

    class Meta:
        model = FileAttachment
        fields = "__all__"
        read_only_fields = ["user", "file_size"]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for messages."""

    sender_name = serializers.CharField(source="sender.name", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_name",
            "content",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["sender", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations."""

    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "participants",
            "title",
            "last_message_at",
            "last_message",
            "unread_count",
            "created_at",
        ]

    def get_last_message(self, obj):
        """Get the last message in the conversation."""
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        """Get the count of unread messages for the current user."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return (
                obj.messages.filter(is_read=False).exclude(sender=request.user).count()
            )
        return 0


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating conversations."""

    participant_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Conversation
        fields = ["title", "participant_ids"]

    def create(self, validated_data):
        """Create a new conversation with participants."""
        participant_ids = validated_data.pop("participant_ids")
        conversation = Conversation.objects.create(**validated_data)
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.set(participants)
        return conversation


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for time slots."""

    instructor_name = serializers.CharField(source="instructor.name", read_only=True)

    class Meta:
        model = TimeSlot
        fields = "__all__"
        read_only_fields = ["instructor"]


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for bookings."""

    student_name = serializers.CharField(source="student.name", read_only=True)
    instructor_name = serializers.CharField(source="instructor.name", read_only=True)
    homestay_title = serializers.CharField(source="homestay.title", read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["student", "created_at", "updated_at"]


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings."""

    class Meta:
        model = Booking
        fields = [
            "instructor",
            "homestay",
            "start_date",
            "end_date",
            "total_amount",
            "notes",
        ]

    def create(self, validated_data):
        """Create a new booking for the current user."""
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["user"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = "__all__"
        read_only_fields = ["user"]


class MarkNotificationsReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""

    notification_ids = serializers.ListField(child=serializers.IntegerField())
