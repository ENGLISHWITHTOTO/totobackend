# Phase 1: Django Backend Implementation Guide

## "English with Toto" - Educational Platform Backend

### 📋 Overview

This document provides a comprehensive guide for implementing the Django backend for the "English with Toto" educational platform. The backend will support user management, content delivery, social features, AI integration, and real-time communication.

### 🏗️ Project Architecture

```
english_with_toto/
├── backend/                    # Django Backend Application
│   ├── config/                 # Django Project Configuration
│   │   ├── __init__.py
│   │   ├── settings/           # Environment-specific settings
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base settings
│   │   │   ├── development.py  # Development settings
│   │   │   └── production.py   # Production settings
│   │   ├── urls.py             # Main URL configuration
│   │   ├── wsgi.py             # WSGI configuration
│   │   └── asgi.py             # ASGI configuration for WebSockets
│   ├── apps/                   # Django Applications
│   │   ├── users/              # User Management & Authentication
│   │   ├── content/            # Educational Content Management
│   │   ├── social/             # Social Features (Moments, Comments, Likes)
│   │   ├── ai/                 # AI Integration for Grammar Checking
│   │   ├── chat/               # Real-time Messaging System
│   │   └── notifications/      # WebSocket Notifications
│   ├── utils/                  # Shared utilities and helpers
│   ├── requirements/           # Dependency management
│   │   ├── base.txt
│   │   ├── development.txt
│   │   └── production.txt
│   ├── manage.py
│   └── .env.example           # Environment variables template
├── mobile-app/                # React Native Mobile Application
├── admin-panel/               # Django Admin or Custom Admin Panel
├── docker-compose.yml         # Multi-container Docker setup
├── Dockerfile                 # Backend container configuration
└── README.md                  # Project documentation
```

### 🎯 Key Features

- **User Management**: Custom user model with role-based access control
- **Content System**: Hierarchical lesson structure with progress tracking
- **Social Platform**: Moments, comments, likes, and follow system
- **AI Integration**: Grammar checking and language assistance
- **Real-time Communication**: WebSocket-based chat and notifications
- **Mobile Support**: API-first design for React Native integration

## 🗄️ Database Models

### 1. 👤 Users App (`apps/users/models.py`)

**Purpose**: Handles user authentication, authorization, and profile management with role-based access control.

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Uses email as the primary identifier instead of username.
    """

    # Role choices for different user types
    ROLE_CHOICES = (
        ('student', _('Student')),
        ('teacher', _('Teacher')),
        ('admin', _('Administrator')),
        ('content_creator', _('Content Creator')),
        ('moderator', _('Moderator')),
    )

    # Language level choices for students
    LANGUAGE_LEVEL_CHOICES = (
        ('beginner', _('Beginner (A1)')),
        ('elementary', _('Elementary (A2)')),
        ('intermediate', _('Intermediate (B1)')),
        ('upper_intermediate', _('Upper Intermediate (B2)')),
        ('advanced', _('Advanced (C1)')),
        ('proficient', _('Proficient (C2)')),
    )

    # Core user fields
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email Address'),
        help_text=_('Required. Enter a valid email address.')
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name=_('User Role')
    )
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Profile Picture'),
        help_text=_('Upload a profile picture (max 2MB)')
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email Verified'),
        help_text=_('Designates whether this user has verified their email.')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Designates whether this user should be treated as active.')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )

    # Remove username field, use email instead
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    Automatically created when a user is created.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('User')
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_('Biography'),
        help_text=_('Tell us about yourself (max 500 characters)')
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of Birth')
    )
    language_level = models.CharField(
        max_length=20,
        choices=User.LANGUAGE_LEVEL_CHOICES,
        blank=True,
        verbose_name=_('English Level'),
        help_text=_('Your current English proficiency level')
    )
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )],
        verbose_name=_('Phone Number')
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        verbose_name=_('Timezone')
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('User Preferences'),
        help_text=_('Store user-specific preferences and settings')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    def get_age(self):
        """Calculate user's age based on date_of_birth."""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

# Signal to create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile automatically when User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
```

### 2. 📚 Content App (`apps/content/models.py`)

**Purpose**: Manages educational content including categories, lessons, exercises, and user progress tracking.

```python
# apps/content/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Category(models.Model):
    """
    Top-level content categories (e.g., Grammar, Vocabulary, Speaking)
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Category Name')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('URL Slug'),
        help_text=_('Used in URLs (e.g., "grammar-basics")')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Brief description of this category')
    )
    image_url = models.URLField(
        blank=True,
        verbose_name=_('Category Image'),
        help_text=_('URL to category cover image')
    )
    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        verbose_name=_('Theme Color'),
        help_text=_('Hex color code for category theme')
    )
    order_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Order'),
        help_text=_('Order in which categories appear')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether this category is visible to users')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order_index', 'name']

    def __str__(self):
        return self.name

    def get_lesson_count(self):
        """Return total number of lessons in this category."""
        return sum(sub.lessons.count() for sub in self.subcategories.all())

class Subcategory(models.Model):
    """
    Subcategories within categories (e.g., Present Tense, Past Tense under Grammar)
    """

    category = models.ForeignKey(
        Category,
        related_name='subcategories',
        on_delete=models.CASCADE,
        verbose_name=_('Parent Category')
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_('Subcategory Name')
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name=_('URL Slug')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=(
            ('beginner', _('Beginner')),
            ('intermediate', _('Intermediate')),
            ('advanced', _('Advanced')),
        ),
        default='beginner',
        verbose_name=_('Difficulty Level')
    )
    estimated_duration = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Estimated Duration (minutes)'),
        help_text=_('Estimated time to complete all lessons in this subcategory')
    )
    order_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Order')
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')
        ordering = ['order_index', 'name']
        unique_together = ['category', 'slug']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class Lesson(models.Model):
    """
    Individual lessons containing educational content and exercises
    """

    subcategory = models.ForeignKey(
        Subcategory,
        related_name='lessons',
        on_delete=models.CASCADE,
        verbose_name=_('Subcategory')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Lesson Title')
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name=_('URL Slug')
    )
    content = models.JSONField(
        verbose_name=_('Lesson Content'),
        help_text=_('Structured content including text, images, videos, and interactive elements')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Brief description of what students will learn')
    )
    learning_objectives = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Learning Objectives'),
        help_text=_('List of what students will achieve after this lesson')
    )
    prerequisites = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='prerequisite_for',
        verbose_name=_('Prerequisites'),
        help_text=_('Lessons that should be completed before this one')
    )
    estimated_duration = models.PositiveIntegerField(
        default=15,
        verbose_name=_('Estimated Duration (minutes)')
    )
    order_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Order')
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['order_index', 'title']
        unique_together = ['subcategory', 'slug']

    def __str__(self):
        return self.title

    def get_exercise_count(self):
        """Return number of exercises in this lesson."""
        return self.exercises.count()

    def get_completion_percentage(self, user):
        """Calculate completion percentage for a specific user."""
        try:
            progress = UserProgress.objects.get(user=user, lesson=self)
            return progress.score
        except UserProgress.DoesNotExist:
            return 0

class Exercise(models.Model):
    """
    Interactive exercises within lessons
    """

    EXERCISE_TYPES = (
        ('multiple_choice', _('Multiple Choice')),
        ('fill_blank', _('Fill in the Blank')),
        ('voice', _('Voice Response')),
        ('drag_drop', _('Drag and Drop')),
        ('matching', _('Matching')),
        ('translation', _('Translation')),
        ('listening', _('Listening Comprehension')),
        ('speaking', _('Speaking Practice')),
    )

    lesson = models.ForeignKey(
        Lesson,
        related_name='exercises',
        on_delete=models.CASCADE,
        verbose_name=_('Lesson')
    )
    type = models.CharField(
        max_length=20,
        choices=EXERCISE_TYPES,
        verbose_name=_('Exercise Type')
    )
    question = models.TextField(
        verbose_name=_('Question/Instruction'),
        help_text=_('The main question or instruction for this exercise')
    )
    data = models.JSONField(
        verbose_name=_('Exercise Data'),
        help_text=_('Structured data including options, correct answers, hints, etc.')
    )
    points = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Points'),
        help_text=_('Points awarded for correct completion')
    )
    time_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Time Limit (seconds)'),
        help_text=_('Optional time limit for completing this exercise')
    )
    order_index = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Display Order')
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Exercise')
        verbose_name_plural = _('Exercises')
        ordering = ['order_index']

    def __str__(self):
        return f"{self.lesson.title} - {self.get_type_display()}"

    def get_correct_answer(self):
        """Extract correct answer from exercise data."""
        return self.data.get('correct_answer', '')

class UserProgress(models.Model):
    """
    Tracks user progress through lessons and exercises
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name=_('User')
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('Lesson')
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_('Completed')
    )
    score = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Score (%)'),
        help_text=_('Percentage score for this lesson')
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Attempts'),
        help_text=_('Number of times user attempted this lesson')
    )
    time_spent = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Time Spent (seconds)'),
        help_text=_('Total time spent on this lesson')
    )
    first_attempted = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('First Attempted')
    )
    last_attempted = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Attempted')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed At')
    )

    class Meta:
        verbose_name = _('User Progress')
        verbose_name_plural = _('User Progress')
        unique_together = ['user', 'lesson']
        ordering = ['-last_attempted']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title} ({self.score}%)"

    def mark_completed(self, score=None):
        """Mark lesson as completed with optional score."""
        from django.utils import timezone

        self.is_completed = True
        if score is not None:
            self.score = score
        if not self.completed_at:
            self.completed_at = timezone.now()
        self.save()

class UserExerciseAttempt(models.Model):
    """
    Tracks individual exercise attempts by users
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='exercise_attempts',
        verbose_name=_('User')
    )
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('Exercise')
    )
    user_answer = models.JSONField(
        verbose_name=_('User Answer'),
        help_text=_('User\'s submitted answer')
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name=_('Correct')
    )
    points_earned = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Points Earned')
    )
    time_taken = models.PositiveIntegerField(
        verbose_name=_('Time Taken (seconds)')
    )
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Attempted At')
    )

    class Meta:
        verbose_name = _('Exercise Attempt')
        verbose_name_plural = _('Exercise Attempts')
        ordering = ['-attempted_at']

    def __str__(self):
        return f"{self.user.email} - {self.exercise} ({'Correct' if self.is_correct else 'Incorrect'})"
```

### 3. 👥 Social App (`apps/social/models.py`)

**Purpose**: Handles social features including moments (posts), comments, likes, follows, and social interactions.

```python
# apps/social/models.py
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Moment(models.Model):
    """
    User-generated content posts (similar to Instagram posts or Facebook statuses)
    """

    MOMENT_TYPES = (
        ('text', _('Text Only')),
        ('image', _('Image')),
        ('video', _('Video')),
        ('achievement', _('Achievement')),
        ('lesson_complete', _('Lesson Completed')),
        ('milestone', _('Milestone')),
    )

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='moments',
        verbose_name=_('Author')
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(1, message=_('Content cannot be empty')),
            MaxLengthValidator(2000, message=_('Content cannot exceed 2000 characters'))
        ],
        verbose_name=_('Content'),
        help_text=_('Share your learning journey, achievements, or thoughts')
    )
    image = models.ImageField(
        upload_to='moments/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Image'),
        help_text=_('Optional image to accompany your moment')
    )
    video = models.FileField(
        upload_to='moments/videos/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Video'),
        help_text=_('Optional video to accompany your moment')
    )
    moment_type = models.CharField(
        max_length=20,
        choices=MOMENT_TYPES,
        default='text',
        verbose_name=_('Moment Type')
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Tags'),
        help_text=_('Hashtags or tags for this moment')
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Public'),
        help_text=_('Whether this moment is visible to all users')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Whether this moment is featured by moderators')
    )
    likes_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Likes Count')
    )
    comments_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Comments Count')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Moment')
        verbose_name_plural = _('Moments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.content[:50]}..."

    def get_likes_count(self):
        """Get the actual count of likes from the database."""
        return self.likes.count()

    def get_comments_count(self):
        """Get the actual count of comments from the database."""
        return self.comments.count()

    def update_counts(self):
        """Update cached counts for likes and comments."""
        self.likes_count = self.get_likes_count()
        self.comments_count = self.get_comments_count()
        self.save(update_fields=['likes_count', 'comments_count'])

class MomentLike(models.Model):
    """
    Tracks likes on moments
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='moment_likes',
        verbose_name=_('User')
    )
    moment = models.ForeignKey(
        Moment,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('Moment')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Moment Like')
        verbose_name_plural = _('Moment Likes')
        unique_together = ['user', 'moment']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} likes {self.moment.id}"

    def save(self, *args, **kwargs):
        """Override save to update moment's like count."""
        super().save(*args, **kwargs)
        self.moment.update_counts()

    def delete(self, *args, **kwargs):
        """Override delete to update moment's like count."""
        super().delete(*args, **kwargs)
        self.moment.update_counts()

class MomentComment(models.Model):
    """
    Comments on moments
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='moment_comments',
        verbose_name=_('User')
    )
    moment = models.ForeignKey(
        Moment,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Moment')
    )
    comment = models.TextField(
        validators=[
            MinLengthValidator(1, message=_('Comment cannot be empty')),
            MaxLengthValidator(500, message=_('Comment cannot exceed 500 characters'))
        ],
        verbose_name=_('Comment')
    )
    parent_comment = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name=_('Parent Comment'),
        help_text=_('For nested comments/replies')
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_('Edited')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Moment Comment')
        verbose_name_plural = _('Moment Comments')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['moment', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.comment[:30]}..."

    def save(self, *args, **kwargs):
        """Override save to update moment's comment count."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.moment.update_counts()

    def delete(self, *args, **kwargs):
        """Override delete to update moment's comment count."""
        super().delete(*args, **kwargs)
        self.moment.update_counts()

class Follow(models.Model):
    """
    User following relationships
    """

    follower = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Follower')
    )
    following = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name=_('Following')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Follow')
        verbose_name_plural = _('Follows')
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f"{self.follower.get_full_name()} follows {self.following.get_full_name()}"

    def clean(self):
        """Prevent users from following themselves."""
        if self.follower == self.following:
            from django.core.exceptions import ValidationError
            raise ValidationError(_('Users cannot follow themselves.'))

class UserActivity(models.Model):
    """
    Track user activities for social features and analytics
    """

    ACTIVITY_TYPES = (
        ('lesson_completed', _('Lesson Completed')),
        ('exercise_completed', _('Exercise Completed')),
        ('achievement_unlocked', _('Achievement Unlocked')),
        ('streak_milestone', _('Streak Milestone')),
        ('level_up', _('Level Up')),
        ('moment_created', _('Moment Created')),
        ('comment_made', _('Comment Made')),
        ('like_given', _('Like Given')),
    )

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('User')
    )
    activity_type = models.CharField(
        max_length=30,
        choices=ACTIVITY_TYPES,
        verbose_name=_('Activity Type')
    )
    description = models.TextField(
        verbose_name=_('Description'),
        help_text=_('Human-readable description of the activity')
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Activity Data'),
        help_text=_('Additional data related to this activity')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.get_activity_type_display()}"

class Notification(models.Model):
    """
    User notifications for social interactions and system events
    """

    NOTIFICATION_TYPES = (
        ('like', _('Like')),
        ('comment', _('Comment')),
        ('follow', _('Follow')),
        ('mention', _('Mention')),
        ('achievement', _('Achievement')),
        ('system', _('System')),
    )

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('User')
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name=_('Type')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    message = models.TextField(
        verbose_name=_('Message')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Read')
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Notification Data'),
        help_text=_('Additional data for the notification')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read'])
```

### 4. 💬 Chat App (`apps/chat/models.py`)

**Purpose**: Handles real-time messaging between users with support for direct messages and group conversations.

```python
# apps/chat/models.py
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.translation import gettext_lazy as _

class Conversation(models.Model):
    """
    Chat conversations between users (can be 1-on-1 or group chats)
    """

    CONVERSATION_TYPES = (
        ('direct', _('Direct Message')),
        ('group', _('Group Chat')),
        ('support', _('Support Chat')),
        ('classroom', _('Classroom Chat')),
    )

    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Conversation Name'),
        help_text=_('Name for group conversations (optional for direct messages)')
    )
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPES,
        default='direct',
        verbose_name=_('Type')
    )
    participants = models.ManyToManyField(
        'users.User',
        related_name='conversations',
        verbose_name=_('Participants')
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_conversations',
        verbose_name=_('Created By')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Whether this conversation is still active')
    )
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Message At')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['-last_message_at']),
            models.Index(fields=['conversation_type', '-last_message_at']),
        ]

    def __str__(self):
        if self.conversation_type == 'direct' and self.participants.count() == 2:
            participants = list(self.participants.all())
            return f"Chat: {participants[0].get_full_name()} & {participants[1].get_full_name()}"
        return self.name or f"Group Chat {self.id}"

    def get_other_participant(self, user):
        """Get the other participant in a direct message conversation."""
        if self.conversation_type == 'direct':
            return self.participants.exclude(id=user.id).first()
        return None

    def update_last_message_time(self):
        """Update the last message timestamp."""
        last_message = self.messages.order_by('-timestamp').first()
        if last_message:
            self.last_message_at = last_message.timestamp
            self.save(update_fields=['last_message_at'])

class Message(models.Model):
    """
    Individual messages within conversations
    """

    MESSAGE_TYPES = (
        ('text', _('Text')),
        ('image', _('Image')),
        ('file', _('File')),
        ('voice', _('Voice Message')),
        ('system', _('System Message')),
    )

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('Conversation')
    )
    sender = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('Sender')
    )
    content = models.TextField(
        validators=[
            MinLengthValidator(1, message=_('Message cannot be empty')),
            MaxLengthValidator(2000, message=_('Message cannot exceed 2000 characters'))
        ],
        verbose_name=_('Content')
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='text',
        verbose_name=_('Type')
    )
    attachment = models.FileField(
        upload_to='chat/attachments/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Attachment'),
        help_text=_('File attachment for the message')
    )
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies',
        verbose_name=_('Reply To'),
        help_text=_('Message this is replying to')
    )
    is_edited = models.BooleanField(
        default=False,
        verbose_name=_('Edited')
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_('Deleted')
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:30]}..."

    def save(self, *args, **kwargs):
        """Override save to update conversation's last message time."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.conversation.update_last_message_time()

class MessageReadStatus(models.Model):
    """
    Track read status of messages by participants
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_status',
        verbose_name=_('Message')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='message_read_status',
        verbose_name=_('User')
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Message Read Status')
        verbose_name_plural = _('Message Read Statuses')
        unique_together = ['message', 'user']
        ordering = ['-read_at']

    def __str__(self):
        return f"{self.user.get_full_name()} read message {self.message.id}"

class TypingIndicator(models.Model):
    """
    Track when users are typing in conversations
    """

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='typing_indicators',
        verbose_name=_('Conversation')
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='typing_indicators',
        verbose_name=_('User')
    )
    is_typing = models.BooleanField(
        default=True,
        verbose_name=_('Is Typing')
    )
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Typing Indicator')
        verbose_name_plural = _('Typing Indicators')
        unique_together = ['conversation', 'user']
        ordering = ['-last_activity']

    def __str__(self):
        status = "typing" if self.is_typing else "not typing"
        return f"{self.user.get_full_name()} is {status} in {self.conversation}"
```

### 5. 🤖 AI App (`apps/ai/models.py`)

**Purpose**: Handles AI integration for grammar checking, language assistance, and intelligent content recommendations.

```python
# apps/ai/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

class AIService(models.Model):
    """
    Configuration for different AI services (OpenAI, Google, etc.)
    """

    SERVICE_TYPES = (
        ('openai', _('OpenAI')),
        ('google', _('Google AI')),
        ('azure', _('Azure OpenAI')),
        ('anthropic', _('Anthropic Claude')),
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Service Name')
    )
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES,
        verbose_name=_('Service Type')
    )
    api_key = models.CharField(
        max_length=500,
        verbose_name=_('API Key'),
        help_text=_('Encrypted API key for the service')
    )
    base_url = models.URLField(
        blank=True,
        verbose_name=_('Base URL'),
        help_text=_('Custom base URL for the API')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    rate_limit_per_minute = models.PositiveIntegerField(
        default=60,
        verbose_name=_('Rate Limit (per minute)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('AI Service')
        verbose_name_plural = _('AI Services')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_service_type_display()})"

class GrammarCheck(models.Model):
    """
    Store grammar check requests and results
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='grammar_checks',
        verbose_name=_('User')
    )
    original_text = models.TextField(
        verbose_name=_('Original Text'),
        help_text=_('The text that was checked')
    )
    corrected_text = models.TextField(
        blank=True,
        verbose_name=_('Corrected Text'),
        help_text=_('AI-suggested corrections')
    )
    suggestions = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Suggestions'),
        help_text=_('Detailed grammar suggestions and explanations')
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_('Confidence Score'),
        help_text=_('AI confidence in the corrections (0-1)')
    )
    language = models.CharField(
        max_length=10,
        default='en',
        verbose_name=_('Language'),
        help_text=_('Language code (e.g., en, es, fr)')
    )
    ai_service = models.ForeignKey(
        AIService,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('AI Service Used')
    )
    processing_time = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Processing Time (seconds)')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Grammar Check')
        verbose_name_plural = _('Grammar Checks')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['language', '-created_at']),
        ]

    def __str__(self):
        return f"Grammar check for {self.user.get_full_name()}: {self.original_text[:50]}..."

class AIUsage(models.Model):
    """
    Track AI usage for billing and rate limiting
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='ai_usage',
        verbose_name=_('User')
    )
    ai_service = models.ForeignKey(
        AIService,
        on_delete=models.CASCADE,
        related_name='usage_records',
        verbose_name=_('AI Service')
    )
    request_type = models.CharField(
        max_length=50,
        verbose_name=_('Request Type'),
        help_text=_('Type of AI request (grammar_check, translation, etc.)')
    )
    tokens_used = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Tokens Used')
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=0,
        verbose_name=_('Cost (USD)')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('AI Usage')
        verbose_name_plural = _('AI Usage Records')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['ai_service', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.request_type} ({self.tokens_used} tokens)"

class ContentRecommendation(models.Model):
    """
    AI-generated content recommendations for users
    """

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='content_recommendations',
        verbose_name=_('User')
    )
    content_type = models.CharField(
        max_length=50,
        choices=(
            ('lesson', _('Lesson')),
            ('exercise', _('Exercise')),
            ('category', _('Category')),
        ),
        verbose_name=_('Content Type')
    )
    content_id = models.PositiveIntegerField(
        verbose_name=_('Content ID'),
        help_text=_('ID of the recommended content')
    )
    recommendation_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        verbose_name=_('Recommendation Score'),
        help_text=_('AI confidence in this recommendation (0-1)')
    )
    reason = models.TextField(
        blank=True,
        verbose_name=_('Reason'),
        help_text=_('Explanation for why this content was recommended')
    )
    is_viewed = models.BooleanField(
        default=False,
        verbose_name=_('Viewed')
    )
    is_clicked = models.BooleanField(
        default=False,
        verbose_name=_('Clicked')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Content Recommendation')
        verbose_name_plural = _('Content Recommendations')
        ordering = ['-recommendation_score', '-created_at']
        unique_together = ['user', 'content_type', 'content_id']
        indexes = [
            models.Index(fields=['user', '-recommendation_score']),
            models.Index(fields=['content_type', 'content_id']),
        ]

    def __str__(self):
        return f"Recommendation for {self.user.get_full_name()}: {self.content_type} #{self.content_id}"

class AIConfiguration(models.Model):
    """
    Global AI configuration settings
    """

    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_('Configuration Key')
    )
    value = models.JSONField(
        verbose_name=_('Configuration Value')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('AI Configuration')
        verbose_name_plural = _('AI Configurations')
        ordering = ['key']

    def __str__(self):
        return f"{self.key}: {self.value}"
```

## ⚙️ Django Configuration

### Settings Structure (`config/settings/`)

**Purpose**: Environment-specific settings for development, staging, and production.

#### Base Settings (`config/settings/base.py`)

```python
# config/settings/base.py
import os
import sys
from datetime import timedelta
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

# Add the project directory to Python path
sys.path.append(str(ROOT_DIR))

def get_env_variable(var_name, default=None):
    """Get environment variable or return default value."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f"Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('SECRET_KEY', 'django-insecure-change-me-in-production')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'channels',
    'django_filters',
    'drf_yasg',  # Swagger documentation
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.users',
    'apps.content',
    'apps.social',
    'apps.ai',
    'apps.chat',
    'apps.notifications',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.users.middleware.JWTAuthenticationMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_variable('DB_NAME', 'english_with_toto'),
        'USER': get_env_variable('DB_USER', 'postgres'),
        'PASSWORD': get_env_variable('DB_PASSWORD', 'password'),
        'HOST': get_env_variable('DB_HOST', 'localhost'),
        'PORT': get_env_variable('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': get_env_variable('DB_SSLMODE', 'prefer'),
        },
    }
}

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ],
    'EXCEPTION_HANDLER': 'apps.utils.exceptions.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React frontend
    "http://localhost:19006", # React Native app
    "http://127.0.0.1:3000",
    "http://127.0.0.1:19006",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# Redis configuration
REDIS_URL = get_env_variable('REDIS_URL', 'redis://localhost:6379/0')

# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            }
        }
    }
}

# Channels configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

# Celery Configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_variable('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = get_env_variable('DEFAULT_FROM_EMAIL', 'noreply@englishwithtoto.com')

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF configuration
CSRF_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Swagger documentation
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
        'post',
        'put',
        'delete',
        'patch'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'list',
    'DEEP_LINKING': True,
    'SHOW_EXTENSIONS': True,
    'SHOW_COMMON_EXTENSIONS': True,
}

# AI Configuration
OPENAI_API_KEY = get_env_variable('OPENAI_API_KEY', '')
AI_RATE_LIMIT_PER_MINUTE = 60
AI_MAX_TOKENS_PER_REQUEST = 4000
AI_DEFAULT_MODEL = 'gpt-3.5-turbo'

# Social features configuration
MOMENTS_PER_PAGE = 20
COMMENTS_PER_PAGE = 10
MAX_MOMENT_LENGTH = 2000
MAX_COMMENT_LENGTH = 500

# Chat configuration
MESSAGE_PER_PAGE = 50
MAX_MESSAGE_LENGTH = 2000
TYPING_INDICATOR_TIMEOUT = 5  # seconds

# Content configuration
LESSONS_PER_PAGE = 20
EXERCISES_PER_PAGE = 10
MAX_CONTENT_LENGTH = 10000
```

#### Development Settings (`config/settings/development.py`)

```python
# config/settings/development.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Development-specific apps
INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

# Development middleware
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Development database (can use SQLite for faster development)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Logging for development
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Cache settings for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Celery settings for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
```

#### Production Settings (`config/settings/production.py`)

```python
# config/settings/production.py
from .base import *

DEBUG = False
ALLOWED_HOSTS = get_env_variable('ALLOWED_HOSTS', '').split(',')

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# Static files for production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files for production (use cloud storage)
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = get_env_variable('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = get_env_variable('AWS_SECRET_ACCESS_KEY')
# AWS_STORAGE_BUCKET_NAME = get_env_variable('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = get_env_variable('AWS_S3_REGION_NAME', 'us-east-1')
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Database for production
DATABASES['default'].update({
    'CONN_MAX_AGE': 60,
    'OPTIONS': {
        'sslmode': 'require',
    }
})

# Redis for production
REDIS_URL = get_env_variable('REDIS_URL')
CACHES['default']['LOCATION'] = REDIS_URL
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]

# Celery for production
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Email for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_variable('EMAIL_HOST')
EMAIL_PORT = int(get_env_variable('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = get_env_variable('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_env_variable('EMAIL_HOST_PASSWORD')

# Logging for production
LOGGING['handlers']['file']['filename'] = '/var/log/django/english_with_toto.log'
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'

# CORS for production
CORS_ALLOWED_ORIGINS = get_env_variable('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# CSRF for production
CSRF_TRUSTED_ORIGINS = get_env_variable('CSRF_TRUSTED_ORIGINS', '').split(',')
```

### URL Configuration (`config/urls.py`)

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="English with Toto API",
        default_version='v1',
        description="API documentation for English with Toto educational platform",
        terms_of_service="https://www.englishwithtoto.com/terms/",
        contact=openapi.Contact(email="api@englishwithtoto.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # API Endpoints
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/content/', include('apps.content.urls')),
    path('api/v1/social/', include('apps.social.urls')),
    path('api/v1/ai/', include('apps.ai.urls')),
    path('api/v1/chat/', include('apps.chat.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),

    # Health check
    path('health/', include('apps.utils.urls')),

    # Redirect root to API docs
    path('', RedirectView.as_view(url='/swagger/', permanent=False)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

## 🚀 Implementation Roadmap

### Phase 1: Core Foundation (Weeks 1-2)

#### 1.1 Project Setup & Database

- [ ] Initialize Django project with proper structure
- [ ] Set up PostgreSQL database
- [ ] Configure Redis for caching and channels
- [ ] Create and run initial migrations
- [ ] Set up environment variables and settings

#### 1.2 User Management System

- [ ] Implement custom User model with email authentication
- [ ] Create UserProfile model with additional fields
- [ ] Set up JWT authentication endpoints
- [ ] Implement user registration and login
- [ ] Add email verification system
- [ ] Create password reset functionality

#### 1.3 Basic API Structure

- [ ] Set up Django REST Framework
- [ ] Create base serializers and viewsets
- [ ] Implement API documentation with Swagger
- [ ] Add proper error handling and validation
- [ ] Set up API versioning

### Phase 2: Content Management (Weeks 3-4)

#### 2.1 Content Models & Admin

- [ ] Implement Category, Subcategory, and Lesson models
- [ ] Create Exercise and UserProgress models
- [ ] Set up Django Admin for content management
- [ ] Add content creation and editing interfaces
- [ ] Implement content ordering and hierarchy

#### 2.2 Content API Endpoints

- [ ] Build CRUD operations for content models
- [ ] Implement content filtering and search
- [ ] Add progress tracking endpoints
- [ ] Create exercise submission and scoring
- [ ] Add content recommendation system

### Phase 3: Social Features (Weeks 5-6)

#### 3.1 Social Models

- [ ] Implement Moment, Comment, and Like models
- [ ] Create Follow and UserActivity models
- [ ] Add Notification system
- [ ] Set up social interaction tracking

#### 3.2 Social API

- [ ] Build Moments API (create, list, like, comment)
- [ ] Implement follow/unfollow system
- [ ] Add social feed generation
- [ ] Create notification endpoints
- [ ] Add social analytics

### Phase 4: AI Integration (Weeks 7-8)

#### 4.1 AI Service Setup

- [ ] Integrate OpenAI API for grammar checking
- [ ] Set up AI service configuration
- [ ] Implement rate limiting and usage tracking
- [ ] Add AI cost monitoring

#### 4.2 AI Features

- [ ] Create grammar check endpoints
- [ ] Implement content recommendations
- [ ] Add language level assessment
- [ ] Build AI-powered feedback system

### Phase 5: Real-time Features (Weeks 9-10)

#### 5.1 WebSocket Setup

- [ ] Configure Django Channels
- [ ] Set up Redis channel layer
- [ ] Create WebSocket consumers
- [ ] Implement connection management

#### 5.2 Real-time Chat

- [ ] Build chat conversation system
- [ ] Implement real-time messaging
- [ ] Add typing indicators
- [ ] Create message read status

#### 5.3 Live Notifications

- [ ] Set up real-time notifications
- [ ] Implement push notifications
- [ ] Add notification preferences
- [ ] Create notification history

### Phase 6: Testing & Optimization (Weeks 11-12)

#### 6.1 Testing

- [ ] Write unit tests for all models
- [ ] Create API endpoint tests
- [ ] Add integration tests
- [ ] Implement performance tests

#### 6.2 Performance Optimization

- [ ] Add database indexing
- [ ] Implement caching strategies
- [ ] Optimize database queries
- [ ] Add API response caching

### Phase 7: Deployment & Monitoring (Weeks 13-14)

#### 7.1 Production Setup

- [ ] Configure production settings
- [ ] Set up Docker containers
- [ ] Implement CI/CD pipeline
- [ ] Configure load balancing

#### 7.2 Monitoring & Analytics

- [ ] Set up application monitoring
- [ ] Add performance metrics
- [ ] Implement error tracking
- [ ] Create analytics dashboard

## 📋 Sample Implementation

### Example View Implementation

```python
# apps/content/views.py
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Prefetch
from django.utils import timezone

from .models import Category, Subcategory, Lesson, Exercise, UserProgress
from .serializers import (
    CategorySerializer, SubcategorySerializer, LessonSerializer,
    ExerciseSerializer, UserProgressSerializer
)
from .filters import LessonFilter, ExerciseFilter
from .permissions import IsContentAccessible

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing content categories.
    Provides list and retrieve operations for categories.
    """
    queryset = Category.objects.filter(is_active=True).prefetch_related(
        Prefetch('subcategories',
                queryset=Subcategory.objects.filter(is_active=True).prefetch_related(
                    Prefetch('lessons',
                            queryset=Lesson.objects.filter(is_active=True))
                ))
    )
    serializer_class = CategorySerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter categories based on user's language level."""
        queryset = super().get_queryset()
        user_level = self.request.user.profile.language_level

        # Filter subcategories by user's language level
        if user_level:
            queryset = queryset.filter(
                subcategories__difficulty_level__lte=user_level
            ).distinct()

        return queryset

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for managing lessons.
    Provides comprehensive lesson management with progress tracking.
    """
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsContentAccessible]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LessonFilter
    search_fields = ['title', 'description', 'content']
    ordering_fields = ['created_at', 'updated_at', 'order_index', 'title']
    ordering = ['order_index']

    def get_queryset(self):
        """Get lessons with user progress information."""
        queryset = Lesson.objects.filter(is_active=True).select_related(
            'subcategory', 'subcategory__category'
        ).prefetch_related(
            'exercises',
            'prerequisites',
            Prefetch('user_progress',
                    queryset=UserProgress.objects.filter(user=self.request.user))
        )

        # Filter by category or subcategory if provided
        category_id = self.request.query_params.get('category')
        subcategory_id = self.request.query_params.get('subcategory')

        if category_id:
            queryset = queryset.filter(subcategory__category_id=category_id)
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Retrieve lesson with user progress information."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Add user progress information
        try:
            progress = instance.user_progress.get(user=request.user)
            progress_data = UserProgressSerializer(progress).data
        except UserProgress.DoesNotExist:
            progress_data = None

        response_data = serializer.data
        response_data['user_progress'] = progress_data

        return Response(response_data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def submit_progress(self, request, pk=None):
        """
        Submit lesson progress and calculate completion status.

        Expected payload:
        {
            "score": 85.5,
            "time_spent": 1200,
            "exercise_attempts": [
                {"exercise_id": 1, "is_correct": true, "time_taken": 30},
                {"exercise_id": 2, "is_correct": false, "time_taken": 45}
            ]
        }
        """
        lesson = self.get_object()
        user = request.user
        data = request.data

        # Validate input data
        score = float(data.get('score', 0))
        time_spent = int(data.get('time_spent', 0))
        exercise_attempts = data.get('exercise_attempts', [])

        if not (0 <= score <= 100):
            return Response(
                {'error': 'Score must be between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate if lesson is completed (e.g., score >= 80%)
        is_completed = score >= 80.0

        # Update or create user progress
        progress, created = UserProgress.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'score': score,
                'is_completed': is_completed,
                'time_spent': time_spent,
                'attempts': models.F('attempts') + 1,
                'last_attempted': timezone.now()
            }
        )

        # Process exercise attempts
        for attempt_data in exercise_attempts:
            try:
                exercise = Exercise.objects.get(
                    id=attempt_data['exercise_id'],
                    lesson=lesson
                )
                # Create or update exercise attempt
                # Implementation details would go here
            except Exercise.DoesNotExist:
                continue

        # Mark as completed if score is sufficient
        if is_completed and not progress.completed_at:
            progress.mark_completed(score)

        # Create activity record
        from apps.social.models import UserActivity
        UserActivity.objects.create(
            user=user,
            activity_type='lesson_completed' if is_completed else 'lesson_attempted',
            description=f"{'Completed' if is_completed else 'Attempted'} lesson: {lesson.title}",
            data={
                'lesson_id': lesson.id,
                'score': score,
                'time_spent': time_spent
            }
        )

        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def exercises(self, request, pk=None):
        """Get all exercises for a specific lesson."""
        lesson = self.get_object()
        exercises = lesson.exercises.filter(is_active=True).order_by('order_index')

        # Apply filters
        exercise_filter = ExerciseFilter(request.GET, queryset=exercises)
        filtered_exercises = exercise_filter.qs

        serializer = ExerciseSerializer(filtered_exercises, many=True)
        return Response(serializer.data)
```

## 🛠️ Development Tools & Commands

### Essential Commands

```bash
# Project setup
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic

# Development server
python manage.py runserver
python manage.py runserver 0.0.0.0:8000  # For external access

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py sqlmigrate app_name migration_number

# Testing
python manage.py test
python manage.py test apps.users
python manage.py test --keepdb  # Keep test database

# Management commands
python manage.py shell
python manage.py dbshell
python manage.py check
python manage.py check --deploy  # Production checks

# Celery tasks
celery -A config worker -l info
celery -A config beat -l info
celery -A config flower  # Web UI for monitoring

# Docker commands
docker-compose up -d
docker-compose down
docker-compose logs -f
docker-compose exec web python manage.py migrate
```

### Environment Variables Template

```bash
# .env.example
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=english_with_toto
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
DB_SSLMODE=prefer

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@englishwithtoto.com

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Production (set these in production)
# ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
# CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📚 Additional Resources

### Recommended Packages

- **django-cors-headers**: CORS support
- **django-filter**: Advanced filtering
- **drf-yasg**: API documentation
- **django-celery-beat**: Periodic tasks
- **django-redis**: Redis caching
- **channels-redis**: Redis channel layer
- **pillow**: Image processing
- **python-decouple**: Environment variables

### Documentation Links

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Django Channels](https://channels.readthedocs.io/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

This comprehensive implementation guide provides everything needed to build a robust, scalable Django backend for the "English with Toto" educational platform. The modular structure, detailed models, and clear implementation roadmap ensure a solid foundation for development.
