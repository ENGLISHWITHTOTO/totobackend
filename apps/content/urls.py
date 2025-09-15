from django.urls import path, URLPattern
from . import views

urlpatterns: list[URLPattern] = [
    # Content URLs will be added here
    # path('categories/', views.CategoryListView.as_view(), name='category_list'),
    # path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
]
