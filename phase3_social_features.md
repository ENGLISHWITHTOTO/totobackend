# Phase 3: Social Features & Real-time Communication

**Duration**: 3-4 weeks  
**Priority**: High  
**Dependencies**: Phase 1 (Core Infrastructure)

## 🎯 Phase Overview

This phase implements social features including voice/video communication, social feed, private messaging, and real-time infrastructure using WebSockets and Django Channels.

## 📋 Phase Goals

- [ ] Public voice rooms with topic-based grouping
- [ ] Random 1-on-1 voice call matching system
- [ ] Private voice/video calls with WebRTC
- [ ] Screen sharing capabilities for teachers
- [ ] Audio quality optimization and echo cancellation
- [ ] Moments feed with multimedia posts
- [ ] Like, comment, and reply system
- [ ] Follow/unfollow functionality
- [ ] Content moderation and reporting system
- [ ] Push notifications for social interactions
- [ ] Real-time text messaging with WebSockets
- [ ] Message threading and conversation management
- [ ] File and media sharing in chats
- [ ] Message encryption and security
- [ ] Read receipts and typing indicators
- [ ] Django Channels with Redis adapter
- [ ] WebSocket connection management
- [ ] Real-time presence tracking
- [ ] Message queuing and delivery guarantees

---

## 🏗️ Implementation Steps

### Step 1: Social Models (Days 1-3)

#### 1.1 Social Features Models

```python
# apps/social/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Moment(models.Model):
    """Social media posts in the Moments feed"""
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('followers', 'Followers Only'),
        ('private', 'Private')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moments')
    content = models.TextField()
    media_files = models.JSONField(default=list)  # List of file URLs
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public')
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'moments'
        verbose_name = _('Moment')
        verbose_name_plural = _('Moments')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.content[:50]}"


class MomentLike(models.Model):
    """Likes on moments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'moment_likes'
        verbose_name = _('Moment Like')
        verbose_name_plural = _('Moment Likes')
        unique_together = ['user', 'moment']

    def __str__(self):
        return f"{self.user.email} likes {self.moment.id}"


class MomentComment(models.Model):
    """Comments on moments"""
    moment = models.ForeignKey(Moment, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'moment_comments'
        verbose_name = _('Moment Comment')
        verbose_name_plural = _('Moment Comments')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.email} commented on {self.moment.id}"


class Follow(models.Model):
    """User follow relationships"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'follows'
        verbose_name = _('Follow')
        verbose_name_plural = _('Follows')
        unique_together = ['follower', 'following']

    def __str__(self):
        return f"{self.follower.email} follows {self.following.email}"


class Report(models.Model):
    """Content and user reports"""
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Account'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed')
    ]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='reports_received')
    reported_moment = models.ForeignKey(Moment, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.reporter.email} - {self.report_type}"
```

### Step 2: Real-time Communication Models (Days 4-6)

#### 2.1 Chat and Messaging Models

```python
# apps/chat/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class ChatRoom(models.Model):
    """Chat rooms for private messaging"""
    ROOM_TYPES = [
        ('private', 'Private'),
        ('group', 'Group'),
        ('voice_room', 'Voice Room')
    ]

    name = models.CharField(max_length=200, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='private')
    participants = models.ManyToManyField(User, related_name='chat_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_rooms'
        verbose_name = _('Chat Room')
        verbose_name_plural = _('Chat Rooms')

    def __str__(self):
        return self.name or f"Room {self.id}"


class Message(models.Model):
    """Chat messages"""
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('file', 'File'),
        ('system', 'System')
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    media_file = models.FileField(upload_to='chat_media/', null=True, blank=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'messages'
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.email} - {self.content[:50]}"


class MessageRead(models.Model):
    """Message read receipts"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_reads'
        verbose_name = _('Message Read')
        verbose_name_plural = _('Message Reads')
        unique_together = ['message', 'user']

    def __str__(self):
        return f"{self.user.email} read message {self.message.id}"


class VoiceRoom(models.Model):
    """Public voice rooms for group speaking practice"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    topic = models.CharField(max_length=100)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    max_participants = models.PositiveIntegerField(default=10)
    current_participants = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voice_rooms'
        verbose_name = _('Voice Room')
        verbose_name_plural = _('Voice Rooms')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class VoiceRoomParticipant(models.Model):
    """Participants in voice rooms"""
    room = models.ForeignKey(VoiceRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False)
    is_speaking = models.BooleanField(default=False)

    class Meta:
        db_table = 'voice_room_participants'
        verbose_name = _('Voice Room Participant')
        verbose_name_plural = _('Voice Room Participants')
        unique_together = ['room', 'user']

    def __str__(self):
        return f"{self.user.email} in {self.room.name}"


class CallSession(models.Model):
    """1-on-1 voice/video call sessions"""
    CALL_TYPES = [
        ('voice', 'Voice Call'),
        ('video', 'Video Call')
    ]

    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('ringing', 'Ringing'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('missed', 'Missed')
    ]

    caller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_made')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calls_received')
    call_type = models.CharField(max_length=20, choices=CALL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(default=0)  # seconds

    class Meta:
        db_table = 'call_sessions'
        verbose_name = _('Call Session')
        verbose_name_plural = _('Call Sessions')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.caller.email} -> {self.receiver.email}"
```

### Step 3: WebSocket Configuration (Days 7-9)

#### 3.1 Django Channels Setup

```python
# config/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
```

#### 3.2 WebSocket Routing

```python
# apps/chat/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\w+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/voice-room/(?P<room_id>\w+)/$', consumers.VoiceRoomConsumer.as_asgi()),
    re_path(r'ws/call/(?P<call_id>\w+)/$', consumers.CallConsumer.as_asgi()),
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
```

#### 3.3 WebSocket Consumers

```python
# apps/chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, Message, MessageRead, VoiceRoom, VoiceRoomParticipant
from apps.social.models import Moment, MomentLike, MomentComment
from apps.notifications.models import Notification


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send recent messages
        await self.send_recent_messages()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'chat_message':
            await self.handle_chat_message(text_data_json)
        elif message_type == 'typing':
            await self.handle_typing(text_data_json)
        elif message_type == 'read_receipt':
            await self.handle_read_receipt(text_data_json)

    async def handle_chat_message(self, data):
        user = self.scope['user']
        if user == AnonymousUser():
            return

        message = await self.save_message(
            user=user,
            content=data['message'],
            message_type=data.get('message_type', 'text'),
            media_file=data.get('media_file')
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': user.email,
                    'content': message.content,
                    'message_type': message.message_type,
                    'created_at': message.created_at.isoformat(),
                    'media_file': message.media_file.url if message.media_file else None
                }
            }
        )

    async def handle_typing(self, data):
        user = self.scope['user']
        if user == AnonymousUser():
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing',
                'user': user.email,
                'is_typing': data['is_typing']
            }
        )

    async def handle_read_receipt(self, data):
        user = self.scope['user']
        if user == AnonymousUser():
            return

        await self.mark_message_read(user, data['message_id'])

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))

    async def typing(self, event):
        # Send typing indicator
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))

    @database_sync_to_async
    def save_message(self, user, content, message_type, media_file=None):
        room = ChatRoom.objects.get(id=self.room_id)
        message = Message.objects.create(
            room=room,
            sender=user,
            content=content,
            message_type=message_type,
            media_file=media_file
        )
        return message

    @database_sync_to_async
    def mark_message_read(self, user, message_id):
        try:
            message = Message.objects.get(id=message_id)
            MessageRead.objects.get_or_create(
                message=message,
                user=user
            )
        except Message.DoesNotExist:
            pass

    @database_sync_to_async
    def send_recent_messages(self):
        room = ChatRoom.objects.get(id=self.room_id)
        messages = Message.objects.filter(room=room).order_by('-created_at')[:50]
        return [
            {
                'id': msg.id,
                'sender': msg.sender.email,
                'content': msg.content,
                'message_type': msg.message_type,
                'created_at': msg.created_at.isoformat(),
                'media_file': msg.media_file.url if msg.media_file else None
            }
            for msg in messages
        ]


class VoiceRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'voice_room_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'join_room':
            await self.handle_join_room(text_data_json)
        elif message_type == 'leave_room':
            await self.handle_leave_room(text_data_json)
        elif message_type == 'audio_data':
            await self.handle_audio_data(text_data_json)
        elif message_type == 'mute_toggle':
            await self.handle_mute_toggle(text_data_json)

    async def handle_join_room(self, data):
        user = self.scope['user']
        if user == AnonymousUser():
            return

        await self.add_participant(user)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participant_joined',
                'user': user.email,
                'participant_count': await self.get_participant_count()
            }
        )

    async def handle_leave_room(self, data):
        user = self.scope['user']
        if user == AnonymousUser():
            return

        await self.remove_participant(user)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'participant_left',
                'user': user.email,
                'participant_count': await self.get_participant_count()
            }
        )

    async def handle_audio_data(self, data):
        # Forward audio data to other participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'audio_data',
                'user': self.scope['user'].email,
                'audio_data': data['audio_data']
            }
        )

    async def handle_mute_toggle(self, data):
        user = self.scope['user']
        if user == AnonymousUser():
            return

        await self.toggle_mute(user, data['is_muted'])

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'mute_toggle',
                'user': user.email,
                'is_muted': data['is_muted']
            }
        )

    @database_sync_to_async
    def add_participant(self, user):
        room = VoiceRoom.objects.get(id=self.room_id)
        participant, created = VoiceRoomParticipant.objects.get_or_create(
            room=room,
            user=user
        )
        if created:
            room.current_participants += 1
            room.save()

    @database_sync_to_async
    def remove_participant(self, user):
        room = VoiceRoom.objects.get(id=self.room_id)
        try:
            participant = VoiceRoomParticipant.objects.get(room=room, user=user)
            participant.delete()
            room.current_participants -= 1
            room.save()
        except VoiceRoomParticipant.DoesNotExist:
            pass

    @database_sync_to_async
    def get_participant_count(self):
        room = VoiceRoom.objects.get(id=self.room_id)
        return room.current_participants

    @database_sync_to_async
    def toggle_mute(self, user, is_muted):
        room = VoiceRoom.objects.get(id=self.room_id)
        try:
            participant = VoiceRoomParticipant.objects.get(room=room, user=user)
            participant.is_muted = is_muted
            participant.save()
        except VoiceRoomParticipant.DoesNotExist:
            pass
```

### Step 4: Social Features APIs (Days 10-12)

#### 4.1 Social Serializers

```python
# apps/social/serializers.py
from rest_framework import serializers
from .models import Moment, MomentLike, MomentComment, Follow, Report
from apps.users.serializers import UserSerializer


class MomentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_following_author = serializers.SerializerMethodField()

    class Meta:
        model = Moment
        fields = '__all__'
        read_only_fields = ('user', 'likes_count', 'comments_count', 'shares_count')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return MomentLike.objects.filter(
                user=request.user,
                moment=obj
            ).exists()
        return False

    def get_is_following_author(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user,
                following=obj.user
            ).exists()
        return False


class MomentCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = MomentComment
        fields = '__all__'
        read_only_fields = ('user', 'likes_count')

    def get_replies(self, obj):
        if obj.parent_comment is None:
            replies = MomentComment.objects.filter(
                parent_comment=obj,
                is_active=True
            ).order_by('created_at')
            return MomentCommentSerializer(replies, many=True).data
        return []


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = '__all__'
        read_only_fields = ('follower',)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ('reporter', 'status', 'admin_notes')
```

#### 4.2 Social Views

```python
# apps/social/views.py
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Moment, MomentLike, MomentComment, Follow, Report
from .serializers import MomentSerializer, MomentCommentSerializer, FollowSerializer, ReportSerializer


class MomentListView(generics.ListCreateAPIView):
    """List and create moments"""
    serializer_class = MomentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get moments from followed users and public moments
        followed_users = Follow.objects.filter(follower=user).values_list('following', flat=True)

        return Moment.objects.filter(
            Q(user__in=followed_users) | Q(visibility='public'),
            is_active=True
        ).select_related('user').prefetch_related('likes', 'comments')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MomentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a moment"""
    serializer_class = MomentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Moment.objects.filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_moment(request, moment_id):
    """Like or unlike a moment"""
    try:
        moment = Moment.objects.get(id=moment_id, is_active=True)
    except Moment.DoesNotExist:
        return Response({'error': 'Moment not found'}, status=status.HTTP_404_NOT_FOUND)

    like, created = MomentLike.objects.get_or_create(
        user=request.user,
        moment=moment
    )

    if created:
        moment.likes_count += 1
        moment.save()
        return Response({'liked': True, 'likes_count': moment.likes_count})
    else:
        like.delete()
        moment.likes_count -= 1
        moment.save()
        return Response({'liked': False, 'likes_count': moment.likes_count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_moment(request, moment_id):
    """Add comment to moment"""
    try:
        moment = Moment.objects.get(id=moment_id, is_active=True)
    except Moment.DoesNotExist:
        return Response({'error': 'Moment not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MomentCommentSerializer(data=request.data)
    if serializer.is_valid():
        comment = serializer.save(user=request.user, moment=moment)
        moment.comments_count += 1
        moment.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """Follow or unfollow a user"""
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if target_user == request.user:
        return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )

    if created:
        return Response({'following': True})
    else:
        follow.delete()
        return Response({'following': False})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def report_content(request):
    """Report content or user"""
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        report = serializer.save(reporter=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

### Step 5: Voice and Video Integration (Days 13-15)

#### 5.1 WebRTC Configuration

```javascript
// Frontend WebRTC configuration
class WebRTCManager {
  constructor() {
    this.localStream = null;
    this.peerConnections = new Map();
    this.iceServers = [
      { urls: "stun:stun.l.google.com:19302" },
      { urls: "stun:stun1.l.google.com:19302" },
    ];
  }

  async initializeLocalStream() {
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      return this.localStream;
    } catch (error) {
      console.error("Error accessing media devices:", error);
      throw error;
    }
  }

  async createPeerConnection(userId) {
    const configuration = {
      iceServers: this.iceServers,
    };

    const peerConnection = new RTCPeerConnection(configuration);

    // Add local stream
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => {
        peerConnection.addTrack(track, this.localStream);
      });
    }

    // Handle remote stream
    peerConnection.ontrack = (event) => {
      const remoteStream = event.streams[0];
      this.handleRemoteStream(remoteStream, userId);
    };

    // Handle ICE candidates
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        this.sendIceCandidate(userId, event.candidate);
      }
    };

    this.peerConnections.set(userId, peerConnection);
    return peerConnection;
  }

  async createOffer(userId) {
    const peerConnection = await this.createPeerConnection(userId);
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    return {
      offer: offer,
      peerConnection: peerConnection,
    };
  }

  async handleOffer(userId, offer) {
    const peerConnection = await this.createPeerConnection(userId);
    await peerConnection.setRemoteDescription(offer);

    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);

    return answer;
  }

  async handleAnswer(userId, answer) {
    const peerConnection = this.peerConnections.get(userId);
    if (peerConnection) {
      await peerConnection.setRemoteDescription(answer);
    }
  }

  async handleIceCandidate(userId, candidate) {
    const peerConnection = this.peerConnections.get(userId);
    if (peerConnection) {
      await peerConnection.addIceCandidate(candidate);
    }
  }

  sendIceCandidate(userId, candidate) {
    // Send ICE candidate via WebSocket
    this.websocket.send(
      JSON.stringify({
        type: "ice_candidate",
        target_user: userId,
        candidate: candidate,
      })
    );
  }

  handleRemoteStream(stream, userId) {
    // Display remote stream in UI
    const videoElement = document.getElementById(`remote-video-${userId}`);
    if (videoElement) {
      videoElement.srcObject = stream;
    }
  }

  async startScreenShare() {
    try {
      const screenStream = await navigator.mediaDevices.getDisplayMedia({
        video: true,
        audio: true,
      });

      // Replace video track in all peer connections
      const videoTrack = screenStream.getVideoTracks()[0];
      this.peerConnections.forEach((peerConnection) => {
        const sender = peerConnection
          .getSenders()
          .find((s) => s.track && s.track.kind === "video");
        if (sender) {
          sender.replaceTrack(videoTrack);
        }
      });

      return screenStream;
    } catch (error) {
      console.error("Error starting screen share:", error);
      throw error;
    }
  }

  async endCall() {
    // Stop all tracks
    if (this.localStream) {
      this.localStream.getTracks().forEach((track) => track.stop());
    }

    // Close all peer connections
    this.peerConnections.forEach((peerConnection) => {
      peerConnection.close();
    });
    this.peerConnections.clear();
  }
}
```

### Step 6: Push Notifications (Days 16-18)

#### 6.1 Notification Models

```python
# apps/notifications/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('message', 'Message'),
        ('call', 'Call'),
        ('lesson_complete', 'Lesson Complete'),
        ('achievement', 'Achievement'),
        ('system', 'System')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)  # Additional data for the notification
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class PushToken(models.Model):
    """User push notification tokens"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=500, unique=True)
    device_type = models.CharField(max_length=20, choices=[
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web')
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'push_tokens'
        verbose_name = _('Push Token')
        verbose_name_plural = _('Push Tokens')

    def __str__(self):
        return f"{self.user.email} - {self.device_type}"
```

#### 6.2 Notification Service

```python
# apps/notifications/services.py
import requests
import json
from django.conf import settings
from django.utils import timezone
from .models import Notification, PushToken


class NotificationService:
    """Handle push notifications"""

    def __init__(self):
        self.fcm_server_key = settings.FCM_SERVER_KEY
        self.fcm_url = 'https://fcm.googleapis.com/fcm/send'

    def send_notification(self, user, notification_type, title, message, data=None):
        """Send notification to user"""
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )

        # Send push notification
        self.send_push_notification(user, notification)

        return notification

    def send_push_notification(self, user, notification):
        """Send push notification via FCM"""
        push_tokens = PushToken.objects.filter(user=user, is_active=True)

        if not push_tokens.exists():
            return

        headers = {
            'Authorization': f'key={self.fcm_server_key}',
            'Content-Type': 'application/json'
        }

        for token in push_tokens:
            payload = {
                'to': token.token,
                'notification': {
                    'title': notification.title,
                    'body': notification.message,
                    'icon': 'default',
                    'sound': 'default'
                },
                'data': notification.data
            }

            try:
                response = requests.post(
                    self.fcm_url,
                    headers=headers,
                    data=json.dumps(payload)
                )

                if response.status_code == 200:
                    notification.is_sent = True
                    notification.save()

            except Exception as e:
                print(f"Error sending push notification: {e}")

    def mark_as_read(self, user, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                user=user,
                id=notification_id
            )
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
```

## ✅ Phase 3 Completion Checklist

- [ ] Social models implemented
- [ ] WebSocket consumers working
- [ ] Real-time messaging functional
- [ ] Voice rooms operational
- [ ] 1-on-1 calls working
- [ ] Moments feed implemented
- [ ] Like/comment system working
- [ ] Follow/unfollow functionality
- [ ] Content reporting system
- [ ] Push notifications working
- [ ] WebRTC integration complete
- [ ] Screen sharing functional
- [ ] Message encryption implemented
- [ ] Read receipts working
- [ ] Typing indicators functional

## 🚀 Next Steps

After completing Phase 3, you'll have:

- Complete social features with real-time communication
- Voice and video calling capabilities
- Social feed with interactions
- Private messaging system
- Push notification system

**Ready to move to Phase 4: Teacher Platform & Marketplace**

---

## 📚 Additional Resources

- [Django Channels](https://channels.readthedocs.io/)
- [WebRTC Documentation](https://webrtc.org/)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [Django REST Framework](https://www.django-rest-framework.org/)
