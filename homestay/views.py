from rest_framework import viewsets, permissions
from django.db.models import Avg
from .models import Homestay, HomestayImage, HomestayReview
from .serializers import (
    HomestaySerializer,
    HomestayImageSerializer,
    HomestayReviewSerializer,
    HomestayCreateSerializer,
)


class HomestayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing homestays.

    Instructors can create and manage their own homestays.
    Students can view active homestays and filter by city.
    """

    serializer_class = HomestaySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return homestays based on user role and filters."""
        user = self.request.user
        queryset = (
            Homestay.objects.filter(is_active=True)
            .select_related("host", "location")
            .prefetch_related("images", "reviews")
        )

        if user.role == "INSTRUCTOR":
            queryset = queryset.filter(host=user)

        city = self.request.query_params.get("city")
        if city:
            queryset = queryset.filter(location__city__icontains=city)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return HomestayCreateSerializer
        return HomestaySerializer

    def perform_create(self, serializer):
        """Ensure only instructors can create homestays."""
        if self.request.user.role != "INSTRUCTOR":
            raise PermissionError("Only instructors can create homestays")
        serializer.save(host=self.request.user)


class HomestayImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing homestay images.

    Instructors can add images to their own homestays.
    """

    serializer_class = HomestayImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return images for homestays owned by current user."""
        return HomestayImage.objects.filter(homestay__host=self.request.user)

    def perform_create(self, serializer):
        """Ensure user can only add images to their own homestays."""
        homestay_id = self.request.data.get("homestay")
        homestay = Homestay.objects.get(id=homestay_id)

        if homestay.host != self.request.user:
            raise PermissionError("You can only add images to your own homestays")

        serializer.save()


class HomestayReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing homestay reviews.

    Students can create reviews for homestays they've stayed at.
    """

    serializer_class = HomestayReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return reviews based on user role."""
        user = self.request.user
        if user.role == "STUDENT":
            return HomestayReview.objects.filter(student=user)
        return HomestayReview.objects.all()

    def perform_create(self, serializer):
        """Ensure only students can create reviews."""
        if self.request.user.role != "STUDENT":
            raise PermissionError("Only students can create reviews")
        serializer.save(student=self.request.user)
