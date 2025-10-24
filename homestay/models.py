from django.db import models
from core.models import TimeStampedModel, User, Location


class Homestay(TimeStampedModel):
    """Homestay model for accommodation listings."""

    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="homestays")
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    max_guests = models.IntegerField(default=1)
    amenities = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "homestay"


class HomestayImage(TimeStampedModel):
    """Homestay image model for photo galleries."""

    homestay = models.ForeignKey(
        Homestay, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="homestays/")
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "homestay_image"


class HomestayReview(TimeStampedModel):
    """Homestay review model for student feedback."""

    homestay = models.ForeignKey(
        Homestay, on_delete=models.CASCADE, related_name="reviews"
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()

    class Meta:
        db_table = "homestay_review"
        unique_together = ["homestay", "student"]
