from rest_framework import viewsets, permissions
from .models import StudentProfile, StudentProgress
from .serializers import StudentProfileSerializer, StudentProgressSerializer


class StudentProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student profiles.

    Students can view and update their own profile.
    Admins can view all student profiles.
    """

    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return student profiles based on user role."""
        user = self.request.user
        if user.role == "STUDENT":
            return StudentProfile.objects.filter(user=user)
        return StudentProfile.objects.all()

    def perform_create(self, serializer):
        """Ensure only students can create student profiles."""
        if self.request.user.role != "STUDENT":
            raise PermissionError("Only students can create student profiles")
        serializer.save(user=self.request.user)


class StudentProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing student progress.

    Students can view and update their own progress.
    Teachers and admins can view all progress records.
    """

    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return student progress based on user role."""
        user = self.request.user
        if user.role == "STUDENT":
            return StudentProgress.objects.filter(student=user)
        return StudentProgress.objects.all()

    def perform_create(self, serializer):
        """Ensure only students can create progress records."""
        if self.request.user.role != "STUDENT":
            raise PermissionError("Only students can create progress records")
        serializer.save(student=self.request.user)
