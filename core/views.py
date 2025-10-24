from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from django.db.models import Q
from django.utils import timezone
from .models import (
    User, Conversation, Message, Booking, TimeSlot, 
    Notification, NotificationPreference
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    ConversationSerializer, MessageSerializer, ConversationCreateSerializer,
    BookingSerializer, TimeSlotSerializer, BookingCreateSerializer,
    NotificationSerializer, NotificationPreferenceSerializer, MarkNotificationsReadSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    
    Allows new users to register with email, name, password, and role.
    Returns user data and JWT tokens upon successful registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    API view for user login.
    
    Authenticates users with email and password.
    Returns user data and JWT tokens upon successful authentication.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
    refresh = RefreshToken.for_user(user)
        
    return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for user profile management.
    
    Allows authenticated users to view and update their profile information.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return the current authenticated user."""
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    API view for listing users.
    
    Returns a paginated list of active users with optional filtering by role
    and search functionality by name and email.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['role']
    search_fields = ['name', 'email']
    
    def get_queryset(self):
        """Return active users."""
        return User.objects.filter(is_active=True)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    
    Provides CRUD operations for conversations and includes custom actions
    for retrieving messages and creating direct chats.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return conversations where the current user is a participant."""
        user = self.request.user
        return Conversation.objects.filter(participants=user).prefetch_related('participants', 'messages')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """Add current user as participant when creating conversation."""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Retrieve messages for a specific conversation.
        
        Returns paginated list of messages in the conversation.
        """
        conversation = self.get_object()
        messages = conversation.messages.all().select_related('sender')
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def direct_chat(self, request):
        """
        Get or create a direct chat with another user.
        
        Requires user_id query parameter to specify the other participant.
        """
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({'error': 'user_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        other_user = User.objects.get(id=other_user_id)
        
        conversation = Conversation.objects.filter(
            participants=user
        ).filter(
            participants=other_user
        ).first()
        
        if not conversation:
            conversation = Conversation.objects.create(title=f"Chat with {other_user.name}")
            conversation.participants.set([user, other_user])
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    
    Provides CRUD operations for messages within conversations
    where the current user is a participant.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return messages from conversations where user is a participant."""
        user = self.request.user
        return Message.objects.filter(
            conversation__participants=user
        ).select_related('sender', 'conversation')
    
    def perform_create(self, serializer):
        """Mark other messages as read when sending a new message."""
        message = serializer.save(sender=self.request.user)
        conversation = message.conversation
        conversation.messages.filter(is_read=False).exclude(
            sender=self.request.user
        ).update(is_read=True)
        conversation.save()


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing time slots.
    
    Instructors can create and manage their availability.
    Students can view available time slots.
    """
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return time slots based on user role."""
        user = self.request.user
        if user.role == 'INSTRUCTOR':
            return TimeSlot.objects.filter(instructor=user)
        return TimeSlot.objects.filter(is_available=True, start_time__gte=timezone.now())
    
    def perform_create(self, serializer):
        """Ensure only instructors can create time slots."""
        if self.request.user.role != 'INSTRUCTOR':
            raise PermissionError("Only instructors can create time slots")
        serializer.save(instructor=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing bookings.
    
    Students can create bookings, instructors can confirm/cancel them.
    Users can only see their own bookings unless they have admin access.
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return bookings based on user role."""
        user = self.request.user
        if user.role == 'STUDENT':
            return Booking.objects.filter(student=user)
        elif user.role == 'INSTRUCTOR':
            return Booking.objects.filter(instructor=user)
        return Booking.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Confirm a booking.
        
        Only the instructor can confirm their bookings.
        """
        booking = self.get_object()
        if booking.instructor != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        booking.status = 'confirmed'
        booking.save()
        return Response({'status': 'booking confirmed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        
        Both student and instructor can cancel bookings.
        """
        booking = self.get_object()
        if booking.student != request.user and booking.instructor != request.user:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        booking.status = 'cancelled'
        booking.save()
        return Response({'status': 'booking cancelled'})


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications.
    
    Users can view their notifications and mark them as read.
    Includes custom actions for bulk operations.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate notification with current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark multiple notifications as read.
        
        Requires notification_ids list in request data.
        """
        serializer = MarkNotificationsReadSerializer(data=request.data)
        if serializer.is_valid():
            notification_ids = serializer.validated_data['notification_ids']
            Notification.objects.filter(
                id__in=notification_ids, 
                user=request.user
            ).update(is_read=True)
            return Response({'status': 'notifications marked as read'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications for current user.
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences.
    
    Users can view and update their notification settings.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notification preferences for current user."""
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate preferences with current user."""
        serializer.save(user=self.request.user)
