from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .serializers import UserSerializer, UserSerializerList 
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated


class RegisterUser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate token for the new user
            token = AccessToken.for_user(user)
            return Response({'user': serializer.data, 'token': str(token)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUser(APIView):
    permission_classes = [AllowAny]  
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Generate an access token for the user
            access_token = AccessToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access_token": str(access_token),
                "username": user.username,
                "role": user.get_role_display(),
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class ReportingManagerListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reporting_managers = User.objects.filter(role=3)  
        serializer = UserSerializerList(reporting_managers, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializerList(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)