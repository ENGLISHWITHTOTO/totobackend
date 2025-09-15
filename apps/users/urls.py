from django.urls import path, URLPattern
from . import views

urlpatterns: list[URLPattern] = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("verify-email/", views.verify_email, name="verify_email"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/", views.reset_password, name="reset_password"),
]
