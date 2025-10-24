from rest_framework import serializers
from .models import Homestay, HomestayImage, HomestayReview
from core.serializers import LocationSerializer, UserSerializer


class HomestayImageSerializer(serializers.ModelSerializer):
    """Serializer for homestay images."""

    class Meta:
        model = HomestayImage
        fields = "__all__"


class HomestayReviewSerializer(serializers.ModelSerializer):
    """Serializer for homestay reviews."""

    student_name = serializers.CharField(source="student.name", read_only=True)

    class Meta:
        model = HomestayReview
        fields = "__all__"
        read_only_fields = ["student"]


class HomestaySerializer(serializers.ModelSerializer):
    """Serializer for homestay data."""

    host_name = serializers.CharField(source="host.name", read_only=True)
    location = LocationSerializer()
    images = HomestayImageSerializer(many=True, read_only=True)
    reviews = HomestayReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Homestay
        fields = "__all__"
        read_only_fields = ["host"]

    def get_average_rating(self, obj):
        """Calculate average rating from reviews."""
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0


class HomestayCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating homestays."""

    location = LocationSerializer()

    class Meta:
        model = Homestay
        fields = [
            "title",
            "description",
            "location",
            "price_per_night",
            "max_guests",
            "amenities",
        ]

    def create(self, validated_data):
        """Create homestay with location."""
        location_data = validated_data.pop("location")
        location = Location.objects.create(**location_data)

        validated_data["host"] = self.context["request"].user
        validated_data["location"] = location
        return super().create(validated_data)
