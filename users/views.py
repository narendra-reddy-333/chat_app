# Create your views here.
from django.contrib.auth import authenticate
from rest_framework import generics, permissions, parsers
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to register
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)  # Add these parsers

    def create(self, request, *args, **kwargs):
        """
        Handles user registration.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise an exception if data is invalid
        user = serializer.save()  # Save the new user
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    View for user login and JWT token generation.
    """
    permission_classes = (permissions.AllowAny,)  # Allow any user to access

    # No need to override post() method as TokenObtainPairView handles
    # token generation and response based on credentials.

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Only authenticated users can update
