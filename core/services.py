from .models import Notification, Conversation, Message, Booking, User


class NotificationService:
    """Service class for handling notification operations."""

    @staticmethod
    def send_notification(user, notification_type, title, message, related_object=None):
        """
        Send a notification to a user.

        Args:
            user: The user to send the notification to
            notification_type: Type of notification (message, booking, payment, system)
            title: Notification title
            message: Notification message
            related_object: Optional related object for context

        Returns:
            Notification: The created notification instance
        """
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_id=related_object.id if related_object else None,
            related_content_type=related_object.__class__.__name__
            if related_object
            else "",
        )
        return notification


class MessagingService:
    """Service class for handling messaging operations."""

    @staticmethod
    def create_conversation(participants, title=""):
        """
        Create a new conversation with participants.

        Args:
            participants: List of User instances to add to the conversation
            title: Optional title for the conversation

        Returns:
            Conversation: The created conversation instance
        """
        conversation = Conversation.objects.create(title=title)
        conversation.participants.set(participants)
        return conversation

    @staticmethod
    def send_message(conversation, sender, content, attachments=None):
        """
        Send a message in a conversation.

        Args:
            conversation: The conversation to send the message in
            sender: The user sending the message
            content: The message content
            attachments: Optional file attachments

        Returns:
            Message: The created message instance
        """
        message = Message.objects.create(
            conversation=conversation, sender=sender, content=content
        )
        conversation.save()
        return message


class BookingService:
    """Service class for handling booking operations."""

    @staticmethod
    def create_booking(
        student, instructor, start_date, end_date, total_amount, homestay=None
    ):
        """
        Create a new booking.

        Args:
            student: The student making the booking
            instructor: The instructor for the booking
            start_date: Start date and time of the booking
            end_date: End date and time of the booking
            total_amount: Total amount for the booking
            homestay: Optional homestay for the booking

        Returns:
            Booking: The created booking instance
        """
        booking = Booking.objects.create(
            student=student,
            instructor=instructor,
            homestay=homestay,
            start_date=start_date,
            end_date=end_date,
            total_amount=total_amount,
        )

        # Send notification to instructor
        NotificationService.send_notification(
            instructor,
            "booking",
            "New Booking Request",
            f"You have a new booking request from {student.name}",
            booking,
        )

        return booking
