from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Custom JWT authentication middleware for Django
    """

    def process_request(self, request):
        # Skip authentication for certain paths
        skip_paths = [
            "/admin/",
            "/api/auth/register/",
            "/api/auth/login/",
            "/api/auth/verify-email/",
            "/api/auth/forgot-password/",
            "/api/auth/reset-password/",
            "/static/",
            "/media/",
        ]

        if any(request.path.startswith(path) for path in skip_paths):
            return None

        # Try to authenticate using JWT
        jwt_auth = JWTAuthentication()
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result:
                request.user, request.auth = auth_result
        except (InvalidToken, TokenError):
            # Token is invalid, user will be anonymous
            pass

        return None
