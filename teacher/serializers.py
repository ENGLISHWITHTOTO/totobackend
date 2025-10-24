from rest_framework import serializers
from .models import Course, Lesson, TeacherProfile
from core.serializers import UserSerializer


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for lesson data."""

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for course data."""

    teacher_name = serializers.CharField(source="teacher.name", read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["teacher"]


class TeacherProfileSerializer(serializers.ModelSerializer):
    """Serializer for teacher profile data."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = "__all__"
