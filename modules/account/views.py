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
from modules.employee.models import Employee
from django.utils.html import format_html
from datetime import timedelta
from django.utils import timezone   
from django.db.models.functions import TruncDate
from django.db import transaction
import random
import logging
from django.db import transaction
from faker import Faker
from django.core.exceptions import ValidationError
import datetime

fake = Faker()

class RegisterUser(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        print("user", request.data)
        if serializer.is_valid():
            try:  
                with transaction.atomic():  # Ensures atomicity
                    # Save the user
                    user = serializer.save()
                    
                    # Retrieve company_id from request payload
                    company_id = request.data.get("company")
                    if not company_id:
                        return Response(
                            {"error": "Company ID is required to create an employee record."},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    emp_code = request.data.get("emp_code")
                    if not emp_code:
                        emp_code = self.generate_emp_code(company_id)

                    first_name = request.data.get('first_name')
                    last_name = request.data.get('last_name')
                    date_of_birth = self.generate_random_date_of_birth()
                    father_name = fake.name()
                    mother_name = fake.name()
                    phone_number = self.generate_random_phone_number()
                    adhaar_number = self.generate_random_adhaar_number()
                    # Create the Employee record
                    Employee.objects.create(
                        user=user,
                        company_id=company_id,
                        emp_code=emp_code, 
                        first_name = first_name,
                        last_name = last_name,
                        date_of_birth=date_of_birth,
                        father_name=father_name,
                        mother_name=mother_name,
                        phone_number=phone_number,
                        adhaar_number=adhaar_number
                    )
                    
                    # Generate token for the new user
                    token = AccessToken.for_user(user)
                    return Response({'user': serializer.data, 'token': str(token)}, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response(
                    {"error": f"Failed to create user and employee record: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @staticmethod
    def generate_emp_code(company_id):
        """Generate a unique emp_code based on the company_id."""
        latest_employee = Employee.objects.filter(company_id=company_id).order_by('-id').first()
        if latest_employee and latest_employee.emp_code:
            # Extract numeric part and increment
            last_code = latest_employee.emp_code
            number = int(''.join(filter(str.isdigit, last_code)))  # Extract numeric part
            new_code = f"EMP{number + 1:03}"  # Increment and format
        else:
            # Start new series if no previous code exists
            new_code = "EMP001"
        return new_code
    
    @staticmethod
    def generate_random_adhaar_number():
        """Generate a random 12-digit Aadhaar number."""
        while True:
            # Generate a 12-digit number
            adhaar_number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            
            # Check if the generated Aadhaar number already exists in the database
            if not Employee.objects.filter(adhaar_number=adhaar_number).exists():
                return adhaar_number

    @staticmethod
    def generate_random_phone_number():
        """Generate a random 10-digit phone number."""
        phone_number = f"9{random.randint(100000000, 999999999)}"  # Ensure valid starting digit
        return phone_number

    @staticmethod
    def generate_random_date_of_birth():
        """Generate a random date of birth between 1980 and 2000."""
        start_date = datetime.date(1980, 1, 1)
        end_date = datetime.date(2000, 12, 31)
        time_between_dates = end_date - start_date
        random_number_of_days = random.randrange(time_between_dates.days)
        random_date = start_date + datetime.timedelta(days=random_number_of_days)
        return random_date


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        
        users = User.objects.select_related('reporting_manager').all()  # Fetch users and their managers efficiently
        
        # Custom logic for including manager names in the serialized response
        user_data = [
            {
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'role': user.get_role_display(),
                'manager_name': user.reporting_manager.get_full_name() if user.reporting_manager else None,
            }
            for user in users
        ]
        
        return Response(user_data)
        

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

# class LoginUser(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):       
#         username = request.data.get('username')
#         password = request.data.get('password')

#         # Authenticate the user
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             # Fetch the Employee object linked to this user
#             try:
#                 employee = Employee.objects.get(user=user)
#                 company = employee.company  # Fetch the related company
#             except Employee.DoesNotExist:
#                 return Response({"error": "Employee details not found for the user"}, status=status.HTTP_404_NOT_FOUND)

#             # Generate an access token for the user
#             access_token = AccessToken.for_user(user)
#             return Response({
#                 "message": "Login successful",
#                 "access_token": str(access_token),
#                 "username": user.username,
#                 "role": user.get_role_display(),
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
  

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
        # send_mail(
        #     subject="Password Reset Request",
        #     message=f"Click the link to reset your password: {reset_link}",
        #     from_email=settings.EMAIL_HOST_USER,
        #     recipient_list=[email],
        # )
        send_mail(
            subject="Password Reset Request",
            message="",  # Empty for text-only fallback
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=format_html(
                """
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f9f9f9;
                    color: #333;
                    }}
                    .email-wrapper {{
                    width: 100%;
                    padding: 20px 0;
                    }}
                    .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                    }}
                    .email-header {{
                    background-color: #007bff;
                    color: #ffffff;
                    text-align: center;
                    padding: 20px;
                    font-size: 20px;
                    font-weight: bold;
                    }}
                    .email-body {{
                    padding: 20px;
                    font-size: 16px;
                    line-height: 1.6;
                    color: #333;
                    }}
                    .email-body p {{
                    margin: 0 0 15px;
                    }}
                    .reset-button {{
                    display: inline-block;
                    background-color: #007bff;
                    color: white;
                    padding: 12px 20px;
                    font-size: 16px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin: 20px 0;
                    text-align: center;
                    }}
                    .reset-button:hover {{
                    background-color: #0056b3;
                    color:white;
                    }}
                    .email-footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    padding: 20px;
                    }}
                </style>
                </head>
                <body>
                <div class="email-wrapper">
                    <div class="email-container">
                    <div class="email-header">
                        Password Reset Request
                    </div>
                    <div class="email-body">
                        <p>Hi <b>{username}</b>,</p>
                        <p>You requested to reset your password. Click the button below to proceed:</p>
                        <a href="{reset_link}" class="reset-button"><span style="color: white;">Reset Password</span></a>
                        <p>If you did not request this, you can safely ignore this email.</p>
                    </div>
                    <div class="email-footer">
                        <p>If you have questions, contact us at <a href="mailto:support@example.com">support@example.com</a>.</p>
                    </div>
                    </div>
                </div>
                </body>
                </html>
                """,
                username=user.username,
                reset_link=reset_link,
            )
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
    
class NewHiresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch the filter type from the query parameters
        filter_type = request.query_params.get('filter_type', 'last_7_days')  # Default to 'last_7_days'
        today = timezone.now().date()  # Only use the date part
        filter_date = None

        # Define the time ranges for different filters
        if filter_type == 'last_7_days':
            filter_date = today - timedelta(days=7)
        elif filter_type == 'last_month':
            filter_date = today - timedelta(days=30)
        elif filter_type == 'last_year':
            filter_date = today - timedelta(days=365)
        elif filter_type == 'ALL':
            filter_date = None  # No filtering required
        else:
            # Handle invalid filter types
            return Response({"detail": "Invalid filter type"}, status=400)

        # Apply filtering based on filter_date or fetch all
        if filter_date is not None:
            new_hires = User.objects.annotate(join_date=TruncDate('date_joined')).filter(join_date__gte=filter_date)
        else:
            new_hires = User.objects.all()  # Fetch all users

        # Serialize the filtered users
        response_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined.date(),  # Include only the date part
                "reporting_manager": user.reporting_manager.id if user.reporting_manager else None,
                "role": user.role.name if hasattr(user.role, 'name') else user.get_role_display()
            }
            for user in new_hires
        ]

        return Response(response_data, status=status.HTTP_200_OK)

    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch the filter type from the query parameters
        filter_type = request.query_params.get('filter_type', 'last_7_days')  # Default to 'last_7_days'
        print("filter type",filter_type)
        today = timezone.now().date()
        print("today", today)
        filter_date = None

        # Define the time ranges for different filters
        if filter_type == 'last_7_days':
            filter_date = today - timedelta(days=7)
        elif filter_type == 'last_month':
            filter_date = today - timedelta(days=30)
        elif filter_type == 'last_year':
            filter_date = today - timedelta(days=365)
        # elif filter_type == 'previous_years':
        #     filter_date = today.replace(year=today.year - 1)
        elif filter_type == 'ALL':
            filter_date = None
        else:
            return Response({"detail": f"Invalid filter type: {filter_type}"}, status=400)


        # Filter users based on the filter date
        if filter_date is not None:
            new_hires = User.objects.annotate(join_date=TruncDate('date_joined')).filter(join_date__gte=filter_date)
        else:
            new_hires = User.objects.all()  # Fetch all users

        # Serialize the filtered users
        response_data = []
        for user in new_hires:
            response_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined,
                "reporting_manager": user.reporting_manager.username if user.reporting_manager else None,
                "role": user.role.name if hasattr(user.role, 'name') else user.get_role_display()  # Adjust based on role type
            })

        return Response(response_data, status=status.HTTP_200_OK)