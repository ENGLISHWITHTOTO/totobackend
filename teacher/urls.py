from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("profiles", views.TeacherProfileViewSet, basename="teacherprofile")
router.register("courses", views.CourseViewSet, basename="course")
router.register("lessons", views.LessonViewSet, basename="lesson")

urlpatterns = [
    path("", include(router.urls)),
]
