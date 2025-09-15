# Phase 1: Core Infrastructure & Authentication

**Duration**: 2-3 weeks  
**Priority**: Critical  
**Dependencies**: None

## 🎯 Phase Overview

This phase establishes the foundational infrastructure for the English with Toto platform, including Django project setup, database configuration, authentication system, and basic user management.

## 📋 Phase Goals

- [ ] Django project structure with environment-specific settings
- [ ] PostgreSQL database setup with connection pooling
- [ ] Redis configuration for caching and sessions
- [ ] Docker containerization with multi-stage builds
- [ ] CI/CD pipeline setup (GitHub Actions)
- [ ] Environment variables and secrets management
- [ ] JWT-based authentication with refresh tokens
- [ ] Social authentication (Google, Facebook, Apple)
- [ ] Email verification and password reset flows
- [ ] Role-based access control (RBAC) system
- [ ] User profile management with avatar uploads
- [ ] Core user models and relationships
- [ ] Content hierarchy (Categories → Subcategories → Lessons)
- [ ] Social features data models
- [ ] Translation and study abroad schemas
- [ ] Database migrations and indexing strategy

---

## 🏗️ Implementation Steps

### Step 1: Project Setup & Configuration (Days 1-3)

#### 1.1 Django Project Structure

```bash
# Create project directory
mkdir english-with-toto
cd english-with-toto

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Django and dependencies
pip install django==5.2.6
pip install djangorestframework==3.16.1
pip install djangorestframework-simplejwt==5.3.0
pip install django-cors-headers==4.8.0
pip install psycopg2-binary==2.9.10
pip install redis==6.4.0
pip install python-decouple==3.8
pip install pillow==11.3.0

# Create Django project
django-admin startproject config .
cd config

# Create Django apps
python manage.py startapp users
python manage.py startapp content
python manage.py startapp social
python manage.py startapp ai
python manage.py startapp chat
python manage.py startapp notifications
python manage.py startapp translation
python manage.py startapp study_abroad
```

#### 1.2 Environment Configuration

```bash
# Create environment files
touch .env.example
touch .env.development
touch .env.production
```

**`.env.example`**

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/totobackend

# Redis
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Social Auth
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=totobackend-media
AWS_S3_REGION_NAME=us-east-1

# OpenAI
OPENAI_API_KEY=your-openai-api-key
```

#### 1.3 Django Settings Structure

```python
# config/settings/__init__.py
from .base import *

# config/settings/base.py
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

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
    'drf_yasg',
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
    'apps.translation',
    'apps.study_abroad',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Middleware
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

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='totobackend'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Redis Configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
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
}

# JWT Configuration
from datetime import timedelta

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
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
    "http://localhost:8081",  # React Native development server
]

CORS_ALLOW_CREDENTIALS = True

# Static and Media Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.User'
```

### Step 2: Database Models (Days 4-6)

#### 2.1 User Models

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Extended user model with additional fields"""
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """Extended user profile information"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('content_creator', 'Content Creator'),
        ('institution', 'Institution'),
        ('homestay', 'Homestay Owner')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    language_preference = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    notification_preferences = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class EmailVerification(models.Model):
    """Email verification tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'email_verifications'
        verbose_name = _('Email Verification')
        verbose_name_plural = _('Email Verifications')

    def __str__(self):
        return f"Verification for {self.user.email}"


class PasswordReset(models.Model):
    """Password reset tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_resets'
        verbose_name = _('Password Reset')
        verbose_name_plural = _('Password Resets')

    def __str__(self):
        return f"Reset for {self.user.email}"
```

#### 2.2 Content Models

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

    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='lessons')
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
        db_table = 'lessons'
        verbose_name = _('Lesson')
        verbose_name_plural = _('Lessons')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Exercise(models.Model):
    """Interactive exercises within lessons"""
    EXERCISE_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('fill_blank', 'Fill in the Blank'),
        ('voice_response', 'Voice Response'),
        ('drag_drop', 'Drag and Drop')
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='exercises')
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES)
    question = models.TextField()
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.JSONField()
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exercises'
        verbose_name = _('Exercise')
        verbose_name_plural = _('Exercises')
        ordering = ['order']

    def __str__(self):
        return f"{self.lesson.title} - {self.question[:50]}"
```

### Step 3: Authentication System (Days 7-9)

#### 3.1 JWT Authentication Views

```python
# apps/users/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, EmailVerification, PasswordReset
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from .utils import send_verification_email, send_password_reset_email
import uuid
from datetime import datetime, timedelta


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=serializer.validated_data.get('role', 'student')
        )

        # Send verification email
        send_verification_email(user)

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'User registered successfully. Please check your email for verification.',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'is_verified': user.is_verified
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User login endpoint"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(username=email, password=password)
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'is_verified': user.is_verified,
                    'role': user.profile.role
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Email verification endpoint"""
    token = request.data.get('token')

    try:
        verification = EmailVerification.objects.get(
            token=token,
            is_used=False,
            expires_at__gt=datetime.now()
        )

        verification.user.is_verified = True
        verification.user.save()

        verification.is_used = True
        verification.save()

        return Response({
            'message': 'Email verified successfully'
        }, status=status.HTTP_200_OK)

    except EmailVerification.DoesNotExist:
        return Response({
            'error': 'Invalid or expired verification token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Password reset request endpoint"""
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
        send_password_reset_email(user)

        return Response({
            'message': 'Password reset email sent'
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Password reset confirmation endpoint"""
    token = request.data.get('token')
    new_password = request.data.get('new_password')

    try:
        reset = PasswordReset.objects.get(
            token=token,
            is_used=False,
            expires_at__gt=datetime.now()
        )

        # Validate password
        try:
            validate_password(new_password, reset.user)
        except ValidationError as e:
            return Response({
                'error': e.messages
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update password
        reset.user.set_password(new_password)
        reset.user.save()

        reset.is_used = True
        reset.save()

        return Response({
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)

    except PasswordReset.DoesNotExist:
        return Response({
            'error': 'Invalid or expired reset token'
        }, status=status.HTTP_400_BAD_REQUEST)
```

#### 3.2 Serializers

```python
# apps/users/serializers.py
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True, required=False, default='student')

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        role = validated_data.pop('role', 'student')

        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('role', 'language_preference', 'timezone', 'notification_preferences', 'is_active')


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'avatar', 'is_verified', 'profile')
        read_only_fields = ('id', 'is_verified')
```

### Step 4: Database Setup & Migrations (Days 10-12)

#### 4.1 Database Configuration

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Install PostgreSQL (macOS)
brew install postgresql
brew services start postgresql

# Install PostgreSQL (Windows)
# Download from https://www.postgresql.org/download/windows/

# Create database
sudo -u postgres psql
CREATE DATABASE totobackend;
CREATE USER totouser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE totobackend TO totouser;
\q
```

#### 4.2 Redis Setup

```bash
# Install Redis (Ubuntu/Debian)
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Redis (macOS)
brew install redis
brew services start redis

# Install Redis (Windows)
# Download from https://github.com/microsoftarchive/redis/releases
```

#### 4.3 Run Migrations

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data
python manage.py loaddata initial_data.json
```

### Step 5: Docker Configuration (Days 13-15)

#### 5.1 Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
```

#### 5.2 Docker Compose

```yaml
# docker-compose.yml
version: "3.8"

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: totobackend
      POSTGRES_USER: totouser
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://totouser:your_password@db:5432/totobackend
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

#### 5.3 Requirements File

```txt
# requirements.txt
Django==5.2.6
djangorestframework==3.16.1
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.8.0
psycopg2-binary==2.9.10
redis==6.4.0
python-decouple==3.8
Pillow==11.3.0
gunicorn==21.2.0
celery==5.3.4
django-celery-beat==2.8.1
django-celery-results==2.6.0
channels==4.3.1
channels-redis==4.3.0
django-filter==23.5
drf-yasg==1.21.10
```

### Step 6: CI/CD Pipeline (Days 16-18)

#### 6.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python manage.py test
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          SECRET_KEY: test-secret-key

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Add your deployment commands here
```

## ✅ Phase 1 Completion Checklist

- [ ] Django project structure created
- [ ] Environment configuration set up
- [ ] Database models implemented
- [ ] Authentication system working
- [ ] JWT tokens generating correctly
- [ ] Email verification functional
- [ ] Password reset working
- [ ] Database migrations applied
- [ ] Docker containers running
- [ ] CI/CD pipeline configured
- [ ] Basic API endpoints tested
- [ ] Admin panel accessible
- [ ] User registration/login working
- [ ] Role-based access control implemented

## 🚀 Next Steps

After completing Phase 1, you'll have:

- A solid Django backend foundation
- Working authentication system
- Database models for core features
- Docker containerization
- CI/CD pipeline
- Basic API endpoints

**Ready to move to Phase 2: Learning System & Content Management**

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Docker Documentation](https://docs.docker.com/)
