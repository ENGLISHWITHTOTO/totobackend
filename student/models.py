from django.db import models
from core.models import TimeStampedModel, User


class StudentProfile(TimeStampedModel):
    """Student profile model for additional student information."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    learning_goals = models.TextField(blank=True)

    class Meta:
        db_table = "student_profile"


class StudentProgress(TimeStampedModel):
    """Student progress tracking model for lessons."""

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey("teacher.Lesson", on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.FloatField(null=True, blank=True)
    time_spent = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_progress"
        unique_together = ["student", "lesson"]
