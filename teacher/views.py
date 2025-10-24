from rest_framework import viewsets, permissions
from .models import Course, Lesson, TeacherProfile
from .serializers import CourseSerializer, LessonSerializer, TeacherProfileSerializer


class TeacherProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing teacher profiles.

    Teachers can view and update their own profile.
    Admins can view all teacher profiles.
    """

    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return teacher profiles based on user role."""
        user = self.request.user
        if user.role == "INSTRUCTOR":
            return TeacherProfile.objects.filter(user=user)
        return TeacherProfile.objects.all()

    def perform_create(self, serializer):
        """Ensure only instructors can create teacher profiles."""
        if self.request.user.role != "INSTRUCTOR":
            raise PermissionError("Only instructors can create teacher profiles")
        serializer.save(user=self.request.user)


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing courses.

    Teachers can create and manage their own courses.
    Students can view published courses.
    """

    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return courses based on user role."""
        user = self.request.user
        if user.role == "INSTRUCTOR":
            return Course.objects.filter(teacher=user)
        return Course.objects.filter(status="published")

    def perform_create(self, serializer):
        """Ensure only instructors can create courses."""
        if self.request.user.role != "INSTRUCTOR":
            raise PermissionError("Only instructors can create courses")
        serializer.save(teacher=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lessons.

    Teachers can create and manage lessons for their courses.
    Students can view published lessons.
    """

    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return lessons based on user role."""
        user = self.request.user
        if user.role == "INSTRUCTOR":
            return Lesson.objects.filter(course__teacher=user)
        return Lesson.objects.filter(is_published=True)
