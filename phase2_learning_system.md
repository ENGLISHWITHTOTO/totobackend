# Phase 2: Learning System & Content Management

**Duration**: 3-4 weeks  
**Priority**: High  
**Dependencies**: Phase 1 (Core Infrastructure)

## 🎯 Phase Overview

This phase focuses on building the core learning system with content management, interactive exercises, AI integration, and vocabulary tools. Students will be able to consume lessons, complete exercises, and track their progress.

## 📋 Phase Goals

- [ ] Hierarchical content organization (Categories → Subcategories → Lessons)
- [ ] Lesson builder with multimedia support (text, images, video, audio)
- [ ] Content versioning and approval workflow
- [ ] File upload and media management with AWS S3
- [ ] Content search and filtering capabilities
- [ ] Multiple Choice Questions (MCQ) system
- [ ] Fill-in-the-blank exercises
- [ ] Voice response tasks with audio recording
- [ ] Drag-and-drop interactive components
- [ ] Exercise scoring and feedback system
- [ ] OpenAI GPT integration for grammar correction
- [ ] Writing evaluation with detailed feedback
- [ ] Real-time AI suggestions and corrections
- [ ] Credit-based AI usage tracking
- [ ] Prompt template management system
- [ ] Personal word bank with categorization
- [ ] Flashcard system with spaced repetition algorithm
- [ ] Vocabulary quiz scheduling and notifications
- [ ] Progress tracking and analytics
- [ ] Learning streak and gamification features

---

## 🏗️ Implementation Steps

### Step 1: Enhanced Content Models (Days 1-3)

#### 1.1 Extended Content Models

```python
# apps/content/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Category(models.Model):
    """Learning content categories"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    """Subcategories within categories"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='subcategory_icons/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subcategories'
        verbose_name = _('Subcategory')
        verbose_name_plural = _('Subcategories')
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class Lesson(models.Model):
    """Individual lessons with multimedia content"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('rejected', 'Rejected')
    ]

    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.JSONField()  # Rich content structure
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    estimated_duration = models.PositiveIntegerField()  # minutes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_lessons')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'lessons'
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LessonMedia(models.Model):
    """Media files associated with lessons"""
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document')
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='media_files')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='lesson_media/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lesson_media'
        verbose_name = _('Lesson Media')
        verbose_name_plural = _('Lesson Media')
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class Exercise(models.Model):
    """Interactive exercises within lessons"""
    EXERCISE_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('fill_blank', 'Fill in the Blank'),
        ('voice_response', 'Voice Response'),
        ('drag_drop', 'Drag and Drop'),
        ('matching', 'Matching'),
        ('true_false', 'True/False')
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES)
    question = models.TextField()
    options = models.JSONField(null=True, blank=True)  # For multiple choice, matching
    correct_answer = models.JSONField()
    explanation = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exercises'
        verbose_name = _('Exercise')
        verbose_name_plural = _('Exercises')
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.question[:50]}"


class ExerciseAttempt(models.Model):
    """Student attempts at exercises"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    answer = models.JSONField()
    is_correct = models.BooleanField()
    score = models.PositiveIntegerField()
    time_spent = models.PositiveIntegerField()  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'exercise_attempts'
        verbose_name = _('Exercise Attempt')
        verbose_name_plural = _('Exercise Attempts')
        unique_together = ['user', 'exercise']

    def __str__(self):
        return f"{self.user.email} - {self.exercise.question[:30]}"


class LessonProgress(models.Model):
    """Student progress through lessons"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completion_percentage = models.PositiveIntegerField(default=0)
    time_spent = models.PositiveIntegerField(default=0)  # seconds
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'lesson_progress'
        verbose_name = _('Lesson Progress')
        verbose_name_plural = _('Lesson Progress')
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.email} - {self.lesson.title}"
```

### Step 2: Vocabulary & Learning Tools (Days 4-6)

#### 2.1 Vocabulary Models

```python
# apps/content/models.py (continued)

class WordBank(models.Model):
    """User's personal word bank"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_bank')
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=200)
    definition = models.TextField(blank=True)
    example_sentence = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ])
    tags = models.JSONField(default=list)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'word_bank'
        verbose_name = _('Word Bank')
        verbose_name_plural = _('Word Bank')
        unique_together = ['user', 'word']

    def __str__(self):
        return f"{self.user.email} - {self.word}"


class Flashcard(models.Model):
    """Flashcards for spaced repetition"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='flashcards')
    word_bank_entry = models.ForeignKey(WordBank, on_delete=models.CASCADE)
    front_text = models.CharField(max_length=200)
    back_text = models.CharField(max_length=200)
    difficulty = models.FloatField(default=2.5)  # SM-2 algorithm
    interval = models.PositiveIntegerField(default=1)  # days
    repetitions = models.PositiveIntegerField(default=0)
    next_review = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'flashcards'
        verbose_name = _('Flashcard')
        verbose_name_plural = _('Flashcards')

    def __str__(self):
        return f"{self.user.email} - {self.front_text}"


class VocabularyQuiz(models.Model):
    """Vocabulary quizzes for spaced repetition"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vocabulary_quizzes')
    flashcards = models.ManyToManyField(Flashcard, through='QuizFlashcard')
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=0.0)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vocabulary_quizzes'
        verbose_name = _('Vocabulary Quiz')
        verbose_name_plural = _('Vocabulary Quizzes')

    def __str__(self):
        return f"{self.user.email} - Quiz {self.id}"


class QuizFlashcard(models.Model):
    """Many-to-many relationship between quizzes and flashcards"""
    quiz = models.ForeignKey(VocabularyQuiz, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    user_answer = models.CharField(max_length=200, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'quiz_flashcards'
        verbose_name = _('Quiz Flashcard')
        verbose_name_plural = _('Quiz Flashcards')
        unique_together = ['quiz', 'flashcard']


class LearningStreak(models.Model):
    """User learning streaks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_streaks')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'learning_streaks'
        verbose_name = _('Learning Streak')
        verbose_name_plural = _('Learning Streaks')

    def __str__(self):
        return f"{self.user.email} - {self.current_streak} days"
```

### Step 3: AI Integration (Days 7-9)

#### 3.1 AI Models

```python
# apps/ai/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class AIService(models.Model):
    """AI services configuration"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    api_endpoint = models.URLField()
    api_key = models.CharField(max_length=200)
    cost_per_token = models.DecimalField(max_digits=10, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_services'
        verbose_name = _('AI Service')
        verbose_name_plural = _('AI Services')

    def __str__(self):
        return self.name


class AIPromptTemplate(models.Model):
    """AI prompt templates"""
    name = models.CharField(max_length=100)
    service = models.ForeignKey(AIService, on_delete=models.CASCADE)
    prompt_template = models.TextField()
    variables = models.JSONField(default=list)  # List of variable names
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_prompt_templates'
        verbose_name = _('AI Prompt Template')
        verbose_name_plural = _('AI Prompt Templates')

    def __str__(self):
        return f"{self.service.name} - {self.name}"


class AIUsageLog(models.Model):
    """Track AI usage for billing and analytics"""
    SERVICE_TYPES = [
        ('grammar_check', 'Grammar Check'),
        ('writing_evaluation', 'Writing Evaluation'),
        ('translation', 'Translation'),
        ('voice_transcription', 'Voice Transcription'),
        ('vocabulary_suggestion', 'Vocabulary Suggestion')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage_logs')
    service = models.ForeignKey(AIService, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    prompt_template = models.ForeignKey(AIPromptTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    input_text = models.TextField()
    output_text = models.TextField()
    input_tokens = models.PositiveIntegerField()
    output_tokens = models.PositiveIntegerField()
    total_tokens = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=4)
    credits_used = models.PositiveIntegerField()
    response_time = models.FloatField()  # seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_usage_logs'
        verbose_name = _('AI Usage Log')
        verbose_name_plural = _('AI Usage Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.service_type}"


class CreditTransaction(models.Model):
    """User credit transactions"""
    TRANSACTION_TYPES = [
        ('purchase', 'Credit Purchase'),
        ('usage', 'AI Usage'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus'),
        ('expired', 'Expired')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Positive for credit, negative for usage
    description = models.TextField()
    ai_usage_log = models.ForeignKey(AIUsageLog, on_delete=models.SET_NULL, null=True, blank=True)
    balance_after = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'credit_transactions'
        verbose_name = _('Credit Transaction')
        verbose_name_plural = _('Credit Transactions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount}"


class UserCredits(models.Model):
    """User credit balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='credits')
    balance = models.PositiveIntegerField(default=0)
    total_purchased = models.PositiveIntegerField(default=0)
    total_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_credits'
        verbose_name = _('User Credits')
        verbose_name_plural = _('User Credits')

    def __str__(self):
        return f"{self.user.email} - {self.balance} credits"
```

#### 3.2 AI Service Implementation

```python
# apps/ai/services.py
import openai
import json
from django.conf import settings
from django.utils import timezone
from .models import AIService, AIPromptTemplate, AIUsageLog, UserCredits, CreditTransaction
import time


class AIServiceManager:
    """Manage AI services and usage"""

    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_grammar_feedback(self, user, text):
        """Get grammar correction feedback"""
        prompt_template = AIPromptTemplate.objects.get(
            name='grammar_check',
            is_active=True
        )

        prompt = prompt_template.prompt_template.format(text=text)

        start_time = time.time()
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        response_time = time.time() - start_time

        output_text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        # Calculate cost
        cost = (total_tokens * 0.00003) / 1000  # Approximate cost per token

        # Log usage
        usage_log = AIUsageLog.objects.create(
            user=user,
            service=AIService.objects.get(name='OpenAI GPT-4'),
            service_type='grammar_check',
            prompt_template=prompt_template,
            input_text=text,
            output_text=output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            credits_used=int(cost * 100),  # 1 credit = $0.01
            response_time=response_time
        )

        # Deduct credits
        self._deduct_credits(user, usage_log.credits_used)

        return {
            'feedback': output_text,
            'credits_used': usage_log.credits_used,
            'remaining_credits': user.credits.balance
        }

    def get_writing_evaluation(self, user, text):
        """Get detailed writing evaluation"""
        prompt_template = AIPromptTemplate.objects.get(
            name='writing_evaluation',
            is_active=True
        )

        prompt = prompt_template.prompt_template.format(text=text)

        start_time = time.time()
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        response_time = time.time() - start_time

        output_text = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        # Calculate cost
        cost = (total_tokens * 0.00003) / 1000

        # Log usage
        usage_log = AIUsageLog.objects.create(
            user=user,
            service=AIService.objects.get(name='OpenAI GPT-4'),
            service_type='writing_evaluation',
            prompt_template=prompt_template,
            input_text=text,
            output_text=output_text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            credits_used=int(cost * 100),
            response_time=response_time
        )

        # Deduct credits
        self._deduct_credits(user, usage_log.credits_used)

        return {
            'evaluation': output_text,
            'credits_used': usage_log.credits_used,
            'remaining_credits': user.credits.balance
        }

    def _deduct_credits(self, user, credits_used):
        """Deduct credits from user balance"""
        user_credits = UserCredits.objects.get(user=user)
        user_credits.balance -= credits_used
        user_credits.total_used += credits_used
        user_credits.save()

        # Create transaction record
        CreditTransaction.objects.create(
            user=user,
            transaction_type='usage',
            amount=-credits_used,
            description=f'AI usage - {credits_used} credits',
            balance_after=user_credits.balance
        )
```

### Step 4: Content Management APIs (Days 10-12)

#### 4.1 Content Serializers

```python
# apps/content/serializers.py
from rest_framework import serializers
from .models import (
    Category, Subcategory, Lesson, LessonMedia, Exercise,
    ExerciseAttempt, LessonProgress, WordBank, Flashcard,
    VocabularyQuiz, LearningStreak
)


class CategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_subcategories_count(self, obj):
        return obj.subcategories.filter(is_active=True).count()


class SubcategorySerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_published=True).count()


class LessonMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonMedia
        fields = '__all__'


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'


class LessonSerializer(serializers.ModelSerializer):
    media_files = LessonMediaSerializer(many=True, read_only=True)
    exercises = ExerciseSerializer(many=True, read_only=True)
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = '__all__'

    def get_progress(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = LessonProgress.objects.get(user=request.user, lesson=obj)
                return {
                    'is_completed': progress.is_completed,
                    'completion_percentage': progress.completion_percentage,
                    'time_spent': progress.time_spent
                }
            except LessonProgress.DoesNotExist:
                return {
                    'is_completed': False,
                    'completion_percentage': 0,
                    'time_spent': 0
                }
        return None


class ExerciseAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseAttempt
        fields = '__all__'
        read_only_fields = ('user', 'is_correct', 'score')


class WordBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordBank
        fields = '__all__'
        read_only_fields = ('user',)


class FlashcardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flashcard
        fields = '__all__'
        read_only_fields = ('user',)


class VocabularyQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyQuiz
        fields = '__all__'
        read_only_fields = ('user', 'total_questions', 'correct_answers', 'score')
```

#### 4.2 Content Views

```python
# apps/content/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import (
    Category, Subcategory, Lesson, Exercise, ExerciseAttempt,
    LessonProgress, WordBank, Flashcard, VocabularyQuiz
)
from .serializers import (
    CategorySerializer, SubcategorySerializer, LessonSerializer,
    ExerciseSerializer, ExerciseAttemptSerializer, WordBankSerializer,
    FlashcardSerializer, VocabularyQuizSerializer
)
from .services import SpacedRepetitionService


class CategoryListView(generics.ListAPIView):
    """List all active categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class SubcategoryListView(generics.ListAPIView):
    """List subcategories for a category"""
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Subcategory.objects.filter(
            category_id=category_id,
            is_active=True
        )


class LessonListView(generics.ListAPIView):
    """List lessons with filtering and search"""
    serializer_class = LessonSerializer

    def get_queryset(self):
        queryset = Lesson.objects.filter(is_published=True)

        # Filter by subcategory
        subcategory_id = self.request.query_params.get('subcategory_id')
        if subcategory_id:
            queryset = queryset.filter(subcategory_id=subcategory_id)

        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset


class LessonDetailView(generics.RetrieveAPIView):
    """Get lesson details"""
    queryset = Lesson.objects.filter(is_published=True)
    serializer_class = LessonSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_exercise(request, exercise_id):
    """Submit exercise answer"""
    try:
        exercise = Exercise.objects.get(id=exercise_id)
    except Exercise.DoesNotExist:
        return Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)

    answer = request.data.get('answer')
    time_spent = request.data.get('time_spent', 0)

    # Check if answer is correct
    is_correct = self._check_answer(exercise, answer)
    score = exercise.points if is_correct else 0

    # Create or update attempt
    attempt, created = ExerciseAttempt.objects.update_or_create(
        user=request.user,
        exercise=exercise,
        defaults={
            'answer': answer,
            'is_correct': is_correct,
            'score': score,
            'time_spent': time_spent
        }
    )

    # Update lesson progress
    self._update_lesson_progress(request.user, exercise.lesson)

    return Response({
        'is_correct': is_correct,
        'score': score,
        'explanation': exercise.explanation,
        'total_score': ExerciseAttempt.objects.filter(
            user=request.user,
            exercise__lesson=exercise.lesson
        ).aggregate(total=models.Sum('score'))['total'] or 0
    })

    def _check_answer(self, exercise, answer):
        """Check if answer is correct based on exercise type"""
        if exercise.exercise_type == 'multiple_choice':
            return answer == exercise.correct_answer
        elif exercise.exercise_type == 'fill_blank':
            return answer.lower().strip() == exercise.correct_answer.lower().strip()
        elif exercise.exercise_type == 'true_false':
            return answer == exercise.correct_answer
        # Add more exercise types as needed
        return False

    def _update_lesson_progress(self, user, lesson):
        """Update user's progress through lesson"""
        progress, created = LessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson
        )

        # Calculate completion percentage
        total_exercises = lesson.exercises.count()
        completed_exercises = ExerciseAttempt.objects.filter(
            user=user,
            exercise__lesson=lesson
        ).count()

        completion_percentage = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        progress.completion_percentage = completion_percentage
        progress.is_completed = completion_percentage >= 100

        if progress.is_completed and not progress.completed_at:
            progress.completed_at = timezone.now()

        progress.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_word_bank(request):
    """Add word to user's word bank"""
    serializer = WordBankSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_word_bank(request):
    """Get user's word bank"""
    words = WordBank.objects.filter(user=request.user)
    serializer = WordBankSerializer(words, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vocabulary_quiz(request):
    """Create vocabulary quiz for user"""
    # Get flashcards due for review
    due_flashcards = Flashcard.objects.filter(
        user=request.user,
        next_review__lte=timezone.now()
    )[:10]  # Limit to 10 questions

    if not due_flashcards.exists():
        return Response({'error': 'No flashcards due for review'}, status=status.HTTP_400_BAD_REQUEST)

    # Create quiz
    quiz = VocabularyQuiz.objects.create(
        user=request.user,
        total_questions=due_flashcards.count()
    )

    # Add flashcards to quiz
    for flashcard in due_flashcards:
        quiz.flashcards.add(flashcard)

    serializer = VocabularyQuizSerializer(quiz)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### Step 5: Spaced Repetition Algorithm (Days 13-15)

#### 5.1 Spaced Repetition Service

```python
# apps/content/services.py
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Flashcard, VocabularyQuiz, QuizFlashcard


class SpacedRepetitionService:
    """Implement SM-2 spaced repetition algorithm"""

    def __init__(self):
        self.quality_threshold = 3  # Minimum quality for successful recall

    def create_flashcard(self, user, word_bank_entry):
        """Create flashcard from word bank entry"""
        flashcard = Flashcard.objects.create(
            user=user,
            word_bank_entry=word_bank_entry,
            front_text=word_bank_entry.word,
            back_text=word_bank_entry.translation,
            next_review=timezone.now()
        )
        return flashcard

    def update_flashcard(self, flashcard, quality):
        """Update flashcard based on user performance"""
        if quality < self.quality_threshold:
            # Failed recall - reset interval
            flashcard.interval = 1
            flashcard.repetitions = 0
        else:
            # Successful recall - update interval
            if flashcard.repetitions == 0:
                flashcard.interval = 1
            elif flashcard.repetitions == 1:
                flashcard.interval = 6
            else:
                flashcard.interval = int(flashcard.interval * flashcard.difficulty)

            flashcard.repetitions += 1

        # Update difficulty
        flashcard.difficulty = self._calculate_difficulty(
            flashcard.difficulty, quality
        )

        # Set next review date
        flashcard.next_review = timezone.now() + timedelta(days=flashcard.interval)
        flashcard.save()

        return flashcard

    def _calculate_difficulty(self, current_difficulty, quality):
        """Calculate new difficulty based on performance"""
        new_difficulty = current_difficulty + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        # Ensure difficulty stays within bounds
        if new_difficulty < 1.3:
            return 1.3
        elif new_difficulty > 2.5:
            return 2.5
        else:
            return new_difficulty

    def get_due_flashcards(self, user, limit=20):
        """Get flashcards due for review"""
        return Flashcard.objects.filter(
            user=user,
            next_review__lte=timezone.now()
        )[:limit]

    def get_learning_streak(self, user):
        """Calculate user's learning streak"""
        from .models import LearningStreak

        streak, created = LearningStreak.objects.get_or_create(user=user)

        # Check if user has activity today
        today = timezone.now().date()
        if streak.last_activity.date() == today:
            return streak.current_streak

        # Check if user had activity yesterday
        yesterday = today - timedelta(days=1)
        if streak.last_activity.date() == yesterday:
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak

        streak.last_activity = timezone.now()
        streak.save()

        return streak.current_streak
```

### Step 6: File Upload & Media Management (Days 16-18)

#### 6.1 AWS S3 Configuration

```python
# config/settings/base.py (add to existing settings)

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3b3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

#### 6.2 File Upload Views

```python
# apps/content/views.py (add to existing views)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_lesson_media(request, lesson_id):
    """Upload media file for lesson"""
    try:
        lesson = Lesson.objects.get(id=lesson_id, created_by=request.user)
    except Lesson.DoesNotExist:
        return Response({'error': 'Lesson not found'}, status=status.HTTP_404_NOT_FOUND)

    file = request.FILES.get('file')
    media_type = request.data.get('media_type')
    title = request.data.get('title', '')
    description = request.data.get('description', '')

    if not file or not media_type:
        return Response({'error': 'File and media type required'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file type
    allowed_types = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'video': ['mp4', 'avi', 'mov', 'wmv'],
        'audio': ['mp3', 'wav', 'ogg', 'm4a'],
        'document': ['pdf', 'doc', 'docx', 'txt']
    }

    file_extension = file.name.split('.')[-1].lower()
    if file_extension not in allowed_types.get(media_type, []):
        return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)

    # Create media object
    media = LessonMedia.objects.create(
        lesson=lesson,
        media_type=media_type,
        file=file,
        title=title,
        description=description
    )

    return Response({
        'id': media.id,
        'file_url': media.file.url,
        'media_type': media.media_type,
        'title': media.title
    }, status=status.HTTP_201_CREATED)
```

## ✅ Phase 2 Completion Checklist

- [ ] Enhanced content models implemented
- [ ] Vocabulary and learning tools created
- [ ] AI integration with OpenAI working
- [ ] Content management APIs functional
- [ ] Spaced repetition algorithm implemented
- [ ] File upload system configured
- [ ] Exercise submission working
- [ ] Progress tracking functional
- [ ] Word bank management working
- [ ] Flashcard system operational
- [ ] Vocabulary quizzes working
- [ ] Learning streaks calculated
- [ ] Credit system integrated
- [ ] AI usage tracking working
- [ ] Media management functional

## 🚀 Next Steps

After completing Phase 2, you'll have:

- Complete learning system with interactive exercises
- AI-powered feedback and evaluation
- Vocabulary tools with spaced repetition
- Progress tracking and analytics
- File upload and media management

**Ready to move to Phase 3: Social Features & Real-time Communication**

---

## 📚 Additional Resources

- [Django File Upload](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/)
- [AWS S3 Integration](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Spaced Repetition Algorithm](https://en.wikipedia.org/wiki/SuperMemo)
- [Django REST Framework](https://www.django-rest-framework.org/)
