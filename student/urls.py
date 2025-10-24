from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("profiles", views.StudentProfileViewSet, basename="studentprofile")
router.register("progress", views.StudentProgressViewSet, basename="studentprogress")

urlpatterns = [
    path("", include(router.urls)),
]
