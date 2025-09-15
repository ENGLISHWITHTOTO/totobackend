from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class Category(models.Model):
    """Learning content categories"""

    name: models.CharField = models.CharField(max_length=100)
    description: models.TextField = models.TextField()
    icon: models.ImageField = models.ImageField(
        upload_to="category_icons/", null=True, blank=True
    )
    order: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Category model."""

        db_table = "categories"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return str(self.name)


class Subcategory(models.Model):
    """Subcategories within categories"""

    category: models.ForeignKey = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )
    name: models.CharField = models.CharField(max_length=100)
    description: models.TextField = models.TextField()
    order: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    is_active: models.BooleanField = models.BooleanField(default=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Subcategory model."""

        db_table = "subcategories"
        verbose_name = _("Subcategory")
        verbose_name_plural = _("Subcategories")
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return f"{self.category.name if self.category else 'Unknown Category'} - {self.name}"


class Lesson(models.Model):
    """Individual lessons with multimedia content"""

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    subcategory: models.ForeignKey = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE, related_name="lessons"
    )
    title: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField()
    content: models.JSONField = models.JSONField()  # Rich content structure
    difficulty_level: models.CharField = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES
    )
    estimated_duration: models.PositiveIntegerField = (
        models.PositiveIntegerField()
    )  # minutes
    is_published: models.BooleanField = models.BooleanField(default=False)
    created_by: models.ForeignKey = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Lesson model."""

        db_table = "lessons"
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return str(self.title)


class Exercise(models.Model):
    """Interactive exercises within lessons"""

    EXERCISE_TYPE_CHOICES = [
        ("multiple_choice", "Multiple Choice"),
        ("fill_blank", "Fill in the Blank"),
        ("voice_response", "Voice Response"),
        ("drag_drop", "Drag and Drop"),
    ]

    lesson: models.ForeignKey = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="exercises"
    )
    exercise_type: models.CharField = models.CharField(
        max_length=50, choices=EXERCISE_TYPE_CHOICES
    )
    question: models.TextField = models.TextField()
    options: models.JSONField = models.JSONField(null=True, blank=True)
    correct_answer: models.JSONField = models.JSONField()
    explanation: models.TextField = models.TextField(blank=True)
    order: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Exercise model."""

        db_table = "exercises"
        verbose_name = _("Exercise")
        verbose_name_plural = _("Exercises")
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.lesson.title if self.lesson else 'Unknown Lesson'} - {self.question}"  # pylint: disable=no-member
