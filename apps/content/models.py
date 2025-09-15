from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Category(models.Model):
    """Learning content categories"""

    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to="category_icons/", null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Subcategories within categories"""

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subcategories"
        verbose_name = _("Subcategory")
        verbose_name_plural = _("Subcategories")
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Lesson(models.Model):
    """Individual lessons with multimedia content"""

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.JSONField()  # Rich content structure
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    estimated_duration = models.PositiveIntegerField()  # minutes
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Exercise(models.Model):
    """Interactive exercises within lessons"""

    EXERCISE_TYPE_CHOICES = [
        ("multiple_choice", "Multiple Choice"),
        ("fill_blank", "Fill in the Blank"),
        ("voice_response", "Voice Response"),
        ("drag_drop", "Drag and Drop"),
    ]

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="exercises"
    )
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES)
    question = models.TextField()
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.JSONField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exercises"
        verbose_name = _("Exercise")
        verbose_name_plural = _("Exercises")
        ordering = ["order"]

    def __str__(self):
        return f"{self.lesson.title} - {self.question}"
