from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
# Authentication
router.register("users", views.UserListView, basename="user")

# Messaging
router.register("conversations", views.ConversationViewSet, basename="conversation")
router.register("messages", views.MessageViewSet, basename="message")

# Bookings
router.register("bookings", views.BookingViewSet, basename="booking")
router.register("time-slots", views.TimeSlotViewSet, basename="timeslot")

# Notifications
router.register("notifications", views.NotificationViewSet, basename="notification")
router.register(
    "notification-preferences",
    views.NotificationPreferenceViewSet,
    basename="notificationpreference",
)

urlpatterns = [
    # Authentication
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    path("login/", views.login_view, name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    # API routes
    path("", include(router.urls)),
]
