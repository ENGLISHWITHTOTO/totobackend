from rest_framework import serializers
from .models import StudentProfile, StudentProgress
from core.serializers import UserSerializer


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile data."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = "__all__"


class StudentProgressSerializer(serializers.ModelSerializer):
    """Serializer for student progress tracking."""

    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = StudentProgress
        fields = "__all__"
        read_only_fields = ["student"]
