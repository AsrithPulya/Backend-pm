#IMPORTS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import date
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee, EmployeeLeavesRequestsDates, Holidays, EmployeeLeavesBalance
from .serializers import LeaveTypeIndexSerializer, LeavePolicyTypesSerializer, EmployeeLeaveRequestSerializer, CompanyMainSerializer, EmployeeSerializer, EmployeeLeavesRequests, ReporteeLeaveBalanceSerializer, HolidaySerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Sum, IntegerField, ExpressionWrapper, DurationField
from datetime import timedelta
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from datetime import datetime
from rest_framework.exceptions import ValidationError
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Sum, F
from django.utils import timezone
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions, generics
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import date
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee, EmployeeLeavesBalance
from .serializers import LeaveTypeIndexSerializer, LeavePolicyTypesSerializer, EmployeeLeaveRequestSerializer, CompanyMainSerializer, EmployeeSerializer, EmployeeLeavesRequests, ProfileSerializer, UserProfileSerializer 
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer
from django.shortcuts import get_object_or_404

from django.core.files.storage import default_storage

from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserFile
from .serializers import UserFileSerializer

class CompanyListCreateAPIView(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanyMainSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = CompanyMainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CreateEmployeeView(APIView):
    def post(self, request):
        # Serialize the incoming data
        serializer = EmployeeSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the employee data if valid
            serializer.save()
            return Response({'message': 'Employee created successfully.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        
        # Return validation errors if the data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class EmployeeListView(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 
class CurrentEmployeeView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view
    def get(self, request):
        # Fetch the employee associated with the current authenticated user
        employee = Employee.objects.get(user=request.user)  
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
class EmployeeViewSet(viewsets.ViewSet):
   
    def list(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

     
    def retrieve(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)

    def create(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    # Delete an employee
    def destroy(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response(status=204)
class UserFileViewSet(viewsets.ModelViewSet):
    queryset = UserFile.objects.all()
    serializer_class = UserFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
         
        return UserFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
       serializer.save(user=self.request.user)


    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_file = request.FILES.get('file', None)

        
        if new_file and instance.file:
            try:
                default_storage.delete(instance.file.path)
            except Exception as e:
                return Response(
                    {"detail": f"Error deleting old file: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

         
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        file_instance = self.get_object()
        if file_instance.user != request.user:
            return Response(
                {"detail": "You are not authorized to delete this file."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
class ProfileView(APIView):
    def get(self, request):
        employees = Employee.objects.all()
        serializer = ProfileSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class EmployeeGetUpdateView(APIView):
    def get(self, request, pk):
        try:
             
            employee = Employee.objects.get(pk=pk)

             
            serializer = EmployeeSerializer(employee, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = EmployeeSerializer(employee, data=request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            employee = Employee.objects.get(user=request.user)
        except Employee.DoesNotExist:
            raise NotFound("Employee profile not found.")

        serializer = UserProfileSerializer(employee)
        return Response(serializer.data, status=200)
    
    def put(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
            serializer = UserProfileSerializer(employee, data=request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

# LEAVE TYPE MANAGEMENT
# Creating a Leave type
class LeaveTypeCreateView(APIView):
    def post(self, request):
        serializer = LeaveTypeIndexSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Leave type created successfully.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Displaying all the Leave types
class LeaveTypeListView(APIView):
    def get(self, request):
        leave_types = LeaveTypeIndex.objects.all()
        serializer = LeaveTypeIndexSerializer(leave_types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# Updating the Leave types
class LeaveTypeUpdateView(APIView):
    def put(self, request, pk):
        leave_type = get_object_or_404(LeaveTypeIndex, pk=pk)
        serializer = LeaveTypeIndexSerializer(leave_type, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Leave type updated successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Deleting a Leave type
class LeaveTypeDeleteView(APIView):
    def delete(self, request, pk):
        leave_type = get_object_or_404(LeaveTypeIndex, pk=pk)
        if leave_type.employeeleavesrequests_set.exists():
            return Response({'message': 'This leave type cannot be deleted as it is associated with leave requests.'}, status=status.HTTP_400_BAD_REQUEST)
        leave_type.delete()
        return Response({'message': 'Leave type deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

# LEAVE POLICY MANAGEMENT
# Creating a Leave Policy
class LeavePolicyCreateView(APIView):
    def post(self, request):
        policy_data = request.data
        policy_serializer = LeavePolicyTypesSerializer(data=policy_data)
        if policy_serializer.is_valid():
            policy_serializer.save()
            return Response(policy_serializer.data, status=status.HTTP_201_CREATED)
        return Response(policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Displaying all the leave policies
class LeavePolicyListView(APIView):
    def get(self, request):
        policy_types = LeavePolicyTypes.objects.all()
        policy_types_serializer = LeavePolicyTypesSerializer(policy_types, many=True)
        return Response({'policy_types': policy_types_serializer.data}, status=status.HTTP_200_OK)
# Updating the Leave Policies
class LeavePolicyUpdateView(APIView):
    def put(self, request, pk):
        policy_type = get_object_or_404(LeavePolicyTypes, pk=pk)
        
        policy_type_data = request.data
        policy_type_serializer = LeavePolicyTypesSerializer(policy_type, data=policy_type_data, partial=True)

        if policy_type_serializer.is_valid():
            policy_type_serializer.save()
            return Response({'message': 'Leave policy updated successfully.'}, status=status.HTTP_200_OK)

        return Response(policy_type_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Deleting the Leave Policies
class LeavePolicyDeleteView(APIView):
    def delete(self, request, pk):
        policy_type = get_object_or_404(LeavePolicyTypes, pk=pk)
        policy_type.delete()
        return Response({'message': 'Leave policy deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

# EMPLOYEE LEAVE BALANCE VIEWS
# View for the employee to see all his Leaves
class EmployeeLeaveBalanceView(APIView):
    def get(self, request):
        try:
            if not hasattr(request.user, 'employee'):
                return Response({"error": "No employee associated with the user."}, status=status.HTTP_400_BAD_REQUEST)

            employee = request.user.employee
            leave_balances = []

            # Fetch leave types for the employee's company
            leave_types = LeaveTypeIndex.objects.filter(company=employee.company)
            if not leave_types:
                return Response({"error": "No leave types found for this company."}, status=status.HTTP_400_BAD_REQUEST)

            for leave_type in leave_types:
                leave_policy = LeavePolicyTypes.objects.filter(leave_type=leave_type).first()
                max_days = leave_policy.max_days if leave_policy else 0

                # Get leave balance or set to max_days if no record
                leave_balance = EmployeeLeavesBalance.objects.filter(employee=employee, leave_type=leave_type).first()
                remaining_balance = leave_balance.remaining_balance if leave_balance else max_days

                # Fetch all approved leave requests for this employee and leave type
                approved_leaves = EmployeeLeavesRequests.objects.filter(
                    employee=employee,
                    leave_type=leave_type,
                    status_of_leave='Approved'
                )
                total_taken = sum(
                    1 if leave_date.leave_day_type == 'Full day' else 0.5
                    for leave_request in approved_leaves
                    for leave_date in leave_request.employee_leaves_requests_dates.all()
                )


                # Append the leave balance data
                leave_balances.append({
                    'leave_type': leave_type.leavename,
                    'total_allocated': max_days,
                    'total_taken': total_taken,
                    'remaining_balance': remaining_balance,
                })

            return Response(leave_balances, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error: {str(e)}")  # Log for debugging
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




# View for Admin to see all the employee leaves
class AdminLeaveBalancesView(APIView):
    def get(self, request):
        leave_balances = []
        employees = Employee.objects.all()

        for employee in employees:
            leave_types = LeaveTypeIndex.objects.filter(company=employee.company)
            for leave_type in leave_types:
                try:
                    max_days = LeavePolicyTypes.objects.get(leave_type=leave_type).max_days
                except LeavePolicyTypes.DoesNotExist:
                    max_days = 0

                total_taken = EmployeeLeavesRequests.objects.filter(leave_type=leave_type, employee=employee, status_of_leave='Approved').count()
                remaining_balance = max_days - total_taken

                leave_balances.append({
                    'employee_code': employee.emp_code,
                    'leave_type': leave_type.leavename,
                    'total_allocated': max_days,
                    'total_taken': total_taken,
                    'remaining_balance': remaining_balance
                })

        return Response(leave_balances, status=status.HTTP_200_OK)

# LEAVE REQUEST VIEWS
# Counting the Business days
def count_business_days(start_date, end_date):
    business_days = 0
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Weekdays are Monday (0) to Friday (4)
            business_days += 1
        current_date += timedelta(days=1)

    # Debug log to ensure the function is working as expected
    print(f"Counting business days from {start_date} to {end_date}: {business_days} days")
    return business_days

LEAVE_DAY_TYPE = [
    ('Half day (1st half)', 'Half day (1st half)'),
    ('Half day (2nd half)', 'Half day (2nd half)'),
    ('Full day', 'Full day'),
]
from datetime import datetime, timedelta
from calendar import day_name
#Apply for a leave view
class ApplyForLeaveView(APIView):
    def post(self, request):
        data = request.data
        employee_id = data.get('employee')
        leave_type_id = data.get('leave_type')
        reporting_manager = data.get('reporting_manager')
        reason_for_leave = data.get('reason_for_leave')
        leave_days = data.get('leave_days')

        # Validate input data
        if not all([employee_id, leave_type_id, reason_for_leave, leave_days]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(leave_days, list) or len(leave_days) == 0:
            return Response({"error": "'leave_days' must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate models
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return Response({"error": "Invalid employee."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_type = LeaveTypeIndex.objects.get(id=leave_type_id)
        except LeaveTypeIndex.DoesNotExist:
            return Response({"error": "Invalid leave type."}, status=status.HTTP_400_BAD_REQUEST)

        leave_policy = LeavePolicyTypes.objects.filter(leave_type=leave_type).first()
        if not leave_policy:
            return Response({"error": f"No policy found for leave type '{leave_type.leavename}'."},
                            status=status.HTTP_400_BAD_REQUEST)

        max_days = leave_policy.max_days

        # Calculate total requested leave days and validate business days
        total_days_requested = 0
        business_days = []
        for day in leave_days:
            leave_date = day.get('date')
            leave_day_type = day.get('leave_day_type')

            if not all([leave_date, leave_day_type]):
                return Response({"error": "Each leave day must have 'date' and 'leave_day_type'."},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                leave_date = datetime.strptime(leave_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": f"Invalid date format for {leave_date}. Use 'YYYY-MM-DD'."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if the date is a weekend
            if leave_date.weekday() in (5, 6):  # Saturday=5, Sunday=6
                business_days.append({"date": leave_date, "status": "Weekend"})
                continue

            if leave_day_type not in dict(LEAVE_DAY_TYPE):
                return Response({"error": f"Invalid leave day type '{leave_day_type}'."},
                                status=status.HTTP_400_BAD_REQUEST)

            business_days.append({"date": leave_date, "status": leave_day_type})
            if leave_day_type in ['Half day (1st half)', 'Half day (2nd half)']:
                total_days_requested += 0.5
            elif leave_day_type == 'Full day':
                total_days_requested += 1

            print(f"Processing leave day: {leave_date}, type: {leave_day_type}")

        # Check if total days exceed the max allowed limit
        existing_leave_days = EmployeeLeavesRequestsDates.objects.filter(
            employee__employee=employee,
            date__gte=datetime.now().date()
        ).count()
        if total_days_requested + existing_leave_days > max_days:
            return Response({"error": f"Total leave days ({total_days_requested + existing_leave_days}) exceed the allowed limit of {max_days}."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if employee has sufficient leave balance
        try:
            leave_balance = EmployeeLeavesBalance.objects.get(employee=employee, leave_type=leave_type)
        except EmployeeLeavesBalance.DoesNotExist:
            return Response({"error": "Employee leave balance not found."}, status=status.HTTP_404_NOT_FOUND)

        if leave_balance.remaining_balance < total_days_requested:
            return Response({
                "error": f"Insufficient leave balance. You have {leave_balance.remaining_balance} days left."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create leave request and dates
        leave_request = EmployeeLeavesRequests.objects.create(
            employee=employee,
            leave_type=leave_type,
            reporting_manager_id=reporting_manager,
            reason_for_leave=reason_for_leave,
            status_of_leave='Pending'
        )

        for business_day in business_days:
            if business_day["status"] != "Weekend":  # Only save non-weekend days
                EmployeeLeavesRequestsDates.objects.create(
                    employee=leave_request,
                    date=business_day["date"],
                    leave_day_type=business_day["status"]
                )

        # Update leave balance
        leave_balance.remaining_balance -= total_days_requested
        leave_balance.save()

        return Response({"message": "Leave request submitted successfully.", "leave_request_id": leave_request.id},
                        status=status.HTTP_201_CREATED)


# View for Employee to see the leave his specifically
class EmployeeLeaveRequestsView(APIView):
    def get(self, request):
        leave_requests = EmployeeLeavesRequests.objects.filter(employee=request.user.employee)
        serializer = EmployeeLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Reportees Leave Requests View
from rest_framework.pagination import PageNumberPagination
class ReporteesLeaveRequestsPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size'
    max_page_size = 100
class ReporteesLeaveRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch reportees' leave requests
        reportees = request.user.reportees.all()  
        leave_requests = EmployeeLeavesRequests.objects.filter(
            employee__user__in=reportees
        ).order_by('-id')

        # Paginate results
        paginator = ReporteesLeaveRequestsPagination()
        paginated_leave_requests = paginator.paginate_queryset(leave_requests, request)

        # Serialize the paginated data
        serializer = EmployeeLeaveRequestSerializer(paginated_leave_requests, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

# View for Admin to see the leaves of employees specifically
class AdminLeaveRequestsView(APIView):
    def get(self, request):
        leave_requests = EmployeeLeavesRequests.objects.all()
        serializer = EmployeeLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
# Admin views for all the Leave requests (ACCEPT/REJECT)
class ViewLeaveRequestView(APIView):
    def get(self, request, pk):
        leave_request = get_object_or_404(EmployeeLeavesRequests, pk=pk)
        serializer = EmployeeLeaveRequestSerializer(leave_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
# Admin can update the Leave requests update(ACCEPT/REJECT)
class UpdateLeaveRequestStatusView(APIView):
    def put(self, request, pk):
        leave_request = get_object_or_404(EmployeeLeavesRequests, pk=pk)
        new_status = request.data.get('status_of_leave')
        leave_request.status_of_leave = new_status
        leave_request.save()
        return Response({'message': 'Leave request status updated successfully.'}, status=status.HTTP_200_OK)

#View for Reporting Manager to Apply or Reject Leaves
class ApproveRejectLeaveRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, leave_id):
        action = request.data.get("action")

        if action not in ["approve", "reject"]:
            return Response({"error": "Invalid action. Action must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = EmployeeLeavesRequests.objects.get(id=leave_id)
        except EmployeeLeavesRequests.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user.id != leave_request.reporting_manager.id:
            return Response({"error": "You are not authorized to approve or reject this leave request."}, status=status.HTTP_403_FORBIDDEN)

        if action == "approve":
            leave_request.status_of_leave = "Approved"
        elif action == "reject":
            leave_request.status_of_leave = "Rejected"

        leave_request.save()

        if action == "approve":
            leave_days = EmployeeLeavesRequestsDates.objects.filter(employee=leave_request.employee)
            if leave_days.exists():
                for leave_day in leave_days:
                    leave_balance, _ = EmployeeLeavesBalance.objects.get_or_create(
                        employee=leave_request.employee,
                        leave_type=leave_request.leave_type
                    )

                    if leave_day.leave_day_type == 'Full day':
                        leave_balance.used_leaves += 1
                    elif leave_day.leave_day_type in ['Half day (1st half)', 'Half day (2nd half)']:
                        leave_balance.used_leaves += 0.5

                    leave_balance.remaining_balance = (
                        leave_balance.remaining_balance - leave_balance.used_leaves
                    )
                    leave_balance.save()

        return Response({
            "message": f"Leave request {action}d successfully."
        }, status=status.HTTP_200_OK)


#View for Fetching the Reportees of a User
class ReporteesListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reporting_manager = request.user
        reportees = Employee.objects.filter(user__reporting_manager=reporting_manager)
        serializer = EmployeeSerializer(reportees, many=True)
        return Response(serializer.data)
#Reportees Leave Balance View
class ReporteesLeaveBalanceView(APIView):
    def get(self, request):
        try:
            leave_balances = []

            # Filter reportees based on the reporting manager (current user)
            reportees = Employee.objects.filter(user__reporting_manager=request.user)

            for reportee in reportees:
                leave_types = LeaveTypeIndex.objects.filter(company=reportee.company)

                for leave_type in leave_types:
                    try:
                        # Fetch the leave policy for the leave type
                        leave_policy = LeavePolicyTypes.objects.get(leave_type=leave_type)
                        max_days = leave_policy.max_days
                    except LeavePolicyTypes.DoesNotExist:
                        # Default policy values if the leave policy is not found
                        max_days = 0

                    # Fetch the leave balance for the reportee and leave type
                    leave_balance = EmployeeLeavesBalance.objects.filter(employee=reportee, leave_type=leave_type).first()

                    # If no leave balance exists, use the default max_days as remaining balance
                    if leave_balance:
                        remaining_balance = leave_balance.remaining_balance
                        total_taken_days = leave_balance.used_leaves
                    else:
                        remaining_balance = max_days
                        total_taken_days = 0

                    # Check if the reportee is on leave today
                    today = timezone.now().date()
                    on_leave_today = EmployeeLeavesRequestsDates.objects.filter(
                        employee__employee=reportee,
                        date=today,
                        employee__leave_type=leave_type,
                        employee__status_of_leave='Approved'
                    ).exists()

                    # Append leave balance details
                    leave_balances.append({
                        'reportee_first_name': reportee.user.first_name,
                        'reportee_last_name': reportee.user.last_name,
                        'leave_type': leave_type.leavename,
                        'total_allocated': max_days,
                        'total_taken': total_taken_days,
                        'remaining_balance': remaining_balance,
                        'on_leave_today': on_leave_today
                    })

            # Return the computed leave balances for reportees
            return Response(leave_balances, status=status.HTTP_200_OK)

        except Exception as e:
            # Return an error response in case of failure
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def reset_leave_balances(request):
    today = datetime.now()
    employees = Employee.objects.all()

    for employee in employees:
        leave_types = LeaveTypeIndex.objects.filter(company=employee.company)
        for leave_type in leave_types:
            try:
                policy = LeavePolicyTypes.objects.get(leave_type=leave_type)
            except LeavePolicyTypes.DoesNotExist:
                continue

            # Check for monthly or quarterly reset conditions
            if policy.carry_forward_type == 'monthly' and today.day == 1:
                reset_leave(employee, leave_type, policy)
            elif policy.carry_forward_type == 'quarterly' and today.month in [1, 4, 7, 10] and today.day == 1:
                reset_leave(employee, leave_type, policy)

    return JsonResponse({'status': 'Leave balances reset successfully'})

def reset_leave(employee, leave_type, policy):
    # Calculate total approved days for the leave type
    total_approved_days = EmployeeLeavesRequests.objects.filter(
        employee=employee,
        leave_type=leave_type,
        status_of_leave='Approved'
    ).aggregate(
        total_days_taken=Sum(
            (F('end_date') - F('start_date')).days + 1
        )
    )['total_days_taken'] or 0  

    # Calculate remaining balance if carry_forward is allowed
    if policy.carry_forward:
        remaining_days = max(0, policy.max_days - total_approved_days)
        carry_forward_limit = 20  # Optional field for maximum carry-forward
        carried_forward_days = min(remaining_days, carry_forward_limit) if carry_forward_limit else remaining_days
        new_leave_balance = policy.max_days + carried_forward_days
    else:
        new_leave_balance = policy.max_days

    print(f"Updated {employee.first_name}'s {leave_type.leavename} balance to {new_leave_balance}")

#TESTING OF THE REQUEST (Manual Reset API)
class TestResetLeaveBalanceView(APIView):
    def post(self, request):
        try:
            current_date = datetime.now().date()

            if current_date.day >= 1:  # Ensure reset happens on the 1st day of the month
                employees = Employee.objects.all()

                for employee in employees:
                    leave_types = LeaveTypeIndex.objects.filter(company=employee.company)

                    for leave_type in leave_types:
                        try:
                            policy = LeavePolicyTypes.objects.get(leave_type=leave_type)
                        except LeavePolicyTypes.DoesNotExist:
                            continue

                        # Calculate total approved days taken for the leave type
                        total_approved_days = EmployeeLeavesRequestsDates.objects.filter(
                            employee__employee=employee,
                            employee__leave_type=leave_type,
                            employee__status_of_leave='Approved'
                        ).count()

                        # Determine remaining balance
                        remaining_balance = max(0, policy.max_days - total_approved_days)

                        # Handle carry-forward logic
                        if policy.carry_forward:
                            carry_forward_limit = 20  # Define carry-forward limit
                            carry_forwarded_days = min(remaining_balance, carry_forward_limit)
                        else:
                            carry_forwarded_days = 0

                        # Reset leave requests and mark them as "Reset"
                        EmployeeLeavesRequests.objects.filter(
                            employee=employee, 
                            leave_type=leave_type, 
                            status_of_leave='Approved'
                        ).update(status_of_leave='Reset')

                        # Optionally update leave balance tracking (if using a separate model/table)

                        # Debug output for logging
                        print(f"Employee: {employee.user.first_name} {employee.user.last_name}")
                        print(f"Leave Type: {leave_type.leavename}")
                        print(f"Remaining Balance: {remaining_balance}")
                        print(f"Carry-Forwarded Days: {carry_forwarded_days}")
                        print(f"New Allocation: {policy.max_days + carry_forwarded_days}")

                # Success response
                return Response({"message": "Leave balances reset successfully with carry-forward logic."}, status=status.HTTP_200_OK)
            else:
                # Return error if the API is called on a day other than the 1st
                return Response({"message": "Reset only happens on the 1st of the month."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Handle errors gracefully
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


#Holidays Views
# Get list of all holidays
class HolidayListView(APIView):
    def get(self, request):
        holidays = Holidays.objects.all()
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get details of a specific holiday
class HolidayDetailView(APIView):
    def get(self, request, pk):
        try:
            holiday = Holidays.objects.get(pk=pk)
        except Holidays.DoesNotExist:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HolidaySerializer(holiday)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            holiday = Holidays.objects.get(pk=pk)
        except Holidays.DoesNotExist:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HolidaySerializer(holiday, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            holiday = Holidays.objects.get(pk=pk)
        except Holidays.DoesNotExist:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)

        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


