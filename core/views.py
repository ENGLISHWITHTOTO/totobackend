from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


# 🔹 Utility function to generate JWT tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# 🔹 User Registration API
@extend_schema(
    tags=["Authentication"],
    operation_id="user_register",
    summary="Register a new user",
    description="Registers a new user (Admin, Instructor, or Student) and returns JWT tokens.",
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer, description="User created successfully"
        ),
        400: OpenApiResponse(description="Validation error"),
    },
    examples=[
        OpenApiExample(
            "Example Registration",
            description="Sample registration request for a student.",
            value={
                "email": "student@example.com",
                "name": "Amanuel Demirew",
                "password": "123456",
                "role": "STUDENT",
            },
        )
    ],
)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(
                {"user": UserSerializer(user).data, "tokens": token},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 User Login API
@extend_schema(
    tags=["Authentication"],
    operation_id="user_login",
    summary="Login user",
    description="Authenticate using email and password to receive access & refresh tokens.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            response=UserSerializer, description="User authenticated successfully"
        ),
        400: OpenApiResponse(description="Invalid credentials"),
    },
    examples=[
        OpenApiExample(
            "Example Login",
            description="Login request with email and password",
            value={"email": "student@example.com", "password": "123456"},
        )
    ],
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token = get_tokens_for_user(user)
            return Response(
                {"user": UserSerializer(user).data, "tokens": token},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 User Profile API (Authenticated)
@extend_schema(
    tags=["Authentication"],
    operation_id="user_profile",
    summary="Get current user profile",
    description="Retrieve the currently authenticated user's information.",
    responses={
        200: OpenApiResponse(
            response=UserSerializer, description="Current user profile retrieved"
        ),
        401: OpenApiResponse(description="Unauthorized - Missing or invalid token"),
    },
)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
