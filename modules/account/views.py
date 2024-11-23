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
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

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
        

# Forgot Password and Reset Password logics
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email") 
        print("request data", request.data) 
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}reset-password?uid={uid}&token={token}"

        # Send email with the reset link
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: {reset_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )

        return Response({"message": "Password reset link sent successfully."}, status=status.HTTP_200_OK)

# Combined "Reset Password" endpoint
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        password = request.data.get("password")

        if not uid or not token or not password:
            return Response({"error": "UID, token, and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(password)
        user.save()
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)