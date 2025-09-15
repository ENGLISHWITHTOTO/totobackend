from django.contrib import admin
from .models import Category, Subcategory, Lesson, Exercise


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("order", "name")


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "order", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "description", "category__name")
    ordering = ("category", "order", "name")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "subcategory",
        "difficulty_level",
        "is_published",
        "created_by",
        "created_at",
    )
    list_filter = (
        "difficulty_level",
        "is_published",
        "created_at",
        "subcategory__category",
    )
    search_fields = ("title", "description", "subcategory__name")
    ordering = ("-created_at",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("question", "lesson", "exercise_type", "order", "created_at")
    list_filter = ("exercise_type", "created_at", "lesson__subcategory__category")
    search_fields = ("question", "lesson__title")
    ordering = ("lesson", "order")
