from django.db import models
from core.models import TimeStampedModel, User, Location


class Course(TimeStampedModel):
    """Course model for teacher courses."""

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    )

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    thumbnail = models.ImageField(upload_to="course_thumbnails/", null=True, blank=True)

    class Meta:
        db_table = "course"


class Lesson(TimeStampedModel):
    """Lesson model for course lessons."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "lesson"
        ordering = ["order"]


class TeacherProfile(TimeStampedModel):
    """Teacher profile model for additional teacher information."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    qualifications = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "teacher_profile"
