from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("homestays", views.HomestayViewSet, basename="homestay")
router.register("images", views.HomestayImageViewSet, basename="homestayimage")
router.register("reviews", views.HomestayReviewViewSet, basename="homestayreview")

urlpatterns = [
    path("", include(router.urls)),
]
