#IMPORTS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import date
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee, EmployeeLeavesRequestsDates, Holidays
from modules.account.models import User
from .serializers import LeaveTypeIndexSerializer, LeavePolicyTypesSerializer, EmployeeLeaveRequestSerializer, CompanyMainSerializer, EmployeeSerializer, EmployeeLeavesRequests, ReporteeLeaveBalanceSerializer, HolidaySerializer, LeavePolicySerializer, LeaveTypeSerializer
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
from django.db.models import Sum, Case, When, FloatField, Q
from django.utils import timezone
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions, generics
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import date
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee
from .serializers import LeaveTypeIndexSerializer, LeavePolicyTypesSerializer, EmployeeLeaveRequestSerializer, CompanyMainSerializer, EmployeeSerializer, EmployeeLeavesRequests, ProfileSerializer, UserProfileSerializer 
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer
from django.shortcuts import get_object_or_404

from django.core.files.storage import default_storage
from django.db import transaction
from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserFile
from .serializers import UserFileSerializer
from modules.account.permssions import IsAdmin, IsEmployee, IsAdminOrManager, IsManager
from rest_framework.decorators import permission_classes

class CompanyListCreateAPIView(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanyMainSerializer(companies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    permission_classes = [IsAdmin]
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
        max_days = policy_data.get('max_days')
        carry_forward_days = policy_data.get('carry_forward_days')
        if carry_forward_days > max_days:
            return Response(
                {"error": "Max days cannot be greater than carry forward days."},
                status=status.HTTP_400_BAD_REQUEST
            )
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

            leave_types = LeaveTypeIndex.objects.filter(company=employee.company)
            for leave_type in leave_types:
                leave_policy = LeavePolicyTypes.objects.filter(leave_type=leave_type).first()
                max_days = leave_policy.max_days if leave_policy else 0

                # Calculate total leaves taken
                approved_leaves = EmployeeLeavesRequests.objects.filter(
                    employee=employee,
                    leave_type=leave_type,
                    # status_of_leave =['Approved']
                    status_of_leave__in=['Approved', 'Pending']
                )
                total_taken = sum(
                    1 if ld.leave_day_type == 'Full day' else 0.5
                    for al in approved_leaves
                    for ld in al.employee_leaves_requests_dates.all()
                )
                # remaining_balance = max_days - total_taken
                remaining_balance = max(max_days - total_taken, 0)

                leave_balances.append({
                    'leave_type': leave_type.leavename,
                    'total_allocated': max_days,
                    # 'leave_type_id':leave_type,
                    'total_taken': total_taken,
                    'remaining_balance': remaining_balance,
                })

            return Response(leave_balances, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# View for Admin to see all the employee leaves
class AdminLeaveBalancesView(APIView):
    permission_classes = [IsAdmin] # Only admin can access this view - working
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

        if not all([employee_id, leave_type_id, reason_for_leave, leave_days]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(leave_days, list) or len(leave_days) == 0:
            return Response({"error": "'leave_days' must be a non-empty list."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            employee = Employee.objects.get(id=employee_id)
            leave_type = LeaveTypeIndex.objects.get(id=leave_type_id)
        except (Employee.DoesNotExist, LeaveTypeIndex.DoesNotExist):
            return Response({"error": "Invalid employee or leave type."}, status=status.HTTP_400_BAD_REQUEST)

        leave_policy = LeavePolicyTypes.objects.filter(leave_type=leave_type).first()
        max_days = leave_policy.max_days if leave_policy else 0

        # Calculate total requested leave days
        total_days_requested = sum(
            0.5 if day.get('leave_day_type') in ['Half day (1st half)', 'Half day (2nd half)'] else 1
            for day in leave_days
        )

        # Check leave balance
        approved_leaves = EmployeeLeavesRequests.objects.filter(
            employee=employee,
            leave_type=leave_type,
            # status_of_leave='Approved'
            status_of_leave__in=['Approved', 'Pending']
        )
        total_taken = sum(
            1 if ld.leave_day_type == 'Full day' else 0.5
            for al in approved_leaves
            for ld in al.employee_leaves_requests_dates.all()
        )

        # remaining_balance = max_days - total_taken
        remaining_balance = max(max_days - total_taken, 0)
        if total_days_requested > remaining_balance:
            return Response({
                "error": f"Insufficient leave balance. Remaining balance: {remaining_balance} days."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create leave request
        leave_request = EmployeeLeavesRequests.objects.create(
            employee=employee,
            leave_type=leave_type,
            reporting_manager_id=reporting_manager,
            reason_for_leave=reason_for_leave,
            status_of_leave='Pending'
        )

        for day in leave_days:
            if day['leave_day_type'] != "Weekend":
                EmployeeLeavesRequestsDates.objects.create(
                    employee=leave_request,
                    date=day['date'],
                    leave_day_type=day['leave_day_type']
                )

        return Response({"message": "Leave request submitted successfully."}, status=status.HTTP_201_CREATED)

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
    permission_classes = [IsAdminOrManager] #working
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
    permission_classes = [IsAdmin] #working
    
    def get(self, request):
        leave_requests = EmployeeLeavesRequests.objects.all()
        serializer = EmployeeLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Admin views for all the Leave requests (ACCEPT/REJECT)
class ViewLeaveRequestView(APIView):
    permission_classes = [IsAdmin] #working
    def get(self, request, pk):
        leave_request = get_object_or_404(EmployeeLeavesRequests, pk=pk)
        serializer = EmployeeLeaveRequestSerializer(leave_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Admin can update the Leave requests update(ACCEPT/REJECT)
class UpdateLeaveRequestStatusView(APIView):
    permission_classes = [IsAdmin] #working
    def put(self, request, pk):
        leave_request = get_object_or_404(EmployeeLeavesRequests, pk=pk)
        new_status = request.data.get('status_of_leave')
        leave_request.status_of_leave = new_status
        leave_request.save()
        return Response({'message': 'Leave request status updated successfully.'}, status=status.HTTP_200_OK)

#View for Reporting Manager to Apply or Reject Leaves
class ApproveRejectLeaveRequest(APIView):
    permission_classes = [IsAdminOrManager] #working

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

            # Process leave dates for approved requests
            leave_days = EmployeeLeavesRequestsDates.objects.filter(employee=leave_request)
            total_days = 0
            for leave_day in leave_days:
                if leave_day.leave_day_type == 'Full day':
                    total_days += 1
                elif leave_day.leave_day_type in ['Half day (1st half)', 'Half day (2nd half)']:
                    total_days += 0.5

            leave_policy = LeavePolicyTypes.objects.filter(leave_type=leave_request.leave_type).first()
            max_days = leave_policy.max_days if leave_policy else 0

            # Fetch total approved leave days for this employee and leave type
            approved_leaves = EmployeeLeavesRequests.objects.filter(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                status_of_leave='Approved'
            )

            # Sum up the total days for all approved leave requests
            total_taken = 0
            for al in approved_leaves:
                # Here, we are fetching the dates related to each approved leave request
                leave_dates = al.employee_leaves_requests_dates.all()
                for ld in leave_dates:
                    if ld.leave_day_type == 'Full day':
                        total_taken += 1
                    elif ld.leave_day_type in ['Half day (1st half)', 'Half day (2nd half)']:
                        total_taken += 0.5

            remaining_balance = max_days - (total_taken + total_days)
            if remaining_balance < 0:
                return Response({
                    "error": "Approving this leave exceeds the employee's leave balance."
                }, status=status.HTTP_400_BAD_REQUEST)

        elif action == "reject":
            leave_request.status_of_leave = "Rejected"

        leave_request.save()
        return Response({"message": f"Leave request {action}d successfully."}, status=status.HTTP_200_OK)

#View for Fetching the Reportees of a User
class ReporteesListView(APIView):
    permission_classes = [IsAdminOrManager] #working
    def get(self, request):
        reporting_manager = request.user
        reportees = Employee.objects.filter(user__reporting_manager=reporting_manager)
        serializer = EmployeeSerializer(reportees, many=True)
        return Response(serializer.data)
    
#Reportees Leave Balance View
class ReporteesLeaveBalanceView(APIView):
    permission_classes = [IsAdminOrManager] #working
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

                    # Calculate total taken days dynamically
                    approved_leave_requests = EmployeeLeavesRequests.objects.filter(
                        employee=reportee,
                        leave_type=leave_type,
                        status_of_leave='Approved'
                    )

                    total_taken_days = sum(
                        1 if leave_date.leave_day_type == 'Full day' else 0.5
                        for leave_request in approved_leave_requests
                        for leave_date in leave_request.employee_leaves_requests_dates.all()
                    )

                    # Calculate remaining balance dynamically
                    remaining_balance = max_days - total_taken_days

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
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        holidays = Holidays.objects.all()
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data)

    # permission_classes = [IsAdminOrManager]
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

    # permission_classes = [IsAdminOrManager]
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

    permission_classes = [IsAdminOrManager]
    def delete(self, request, pk):
        try:
            holiday = Holidays.objects.get(pk=pk)
        except Holidays.DoesNotExist:
            return Response({"error": "Holiday not found"}, status=status.HTTP_404_NOT_FOUND)

        holiday.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# class EmployeeQuarterlyLeaveRequestView(generics.ListAPIView):
#     serializer_class = EmployeeLeaveRequestSerializer
    
#     def get_queryset(self):
#         # Get the employee and leave type from the request params
#         employee_id = self.kwargs['employee_id']
#         leave_type_id = self.kwargs['leave_type_id']
        
#         # Get the quarter from the query params
#         quarter = self.request.query_params.get('quarter', None)
        
#         # Get the current year
#         current_year = datetime.now().year
        
#         # date ranges for each quarter
#         if quarter == 'Q1':
#             start_date = datetime(current_year, 1, 1) #JAN
#             end_date = datetime(current_year, 3, 31) #MAR
#         elif quarter == 'Q2':
#             start_date = datetime(current_year, 4, 1) #APR
#             end_date = datetime(current_year, 6, 30) #JUN
#         elif quarter == 'Q3':
#             start_date = datetime(current_year, 7, 1) #JULY
#             end_date = datetime(current_year, 9, 30)  #Sept
#         elif quarter == 'Q4':
#             start_date = datetime(current_year, 10, 1) #OCT
#             end_date = datetime(current_year, 12, 31)  #DEC
#         else:
#             # If no quarter is specified, return all leaves for the given employee and leave type
#             return EmployeeLeavesRequests.objects.filter(
#                 employee_id=employee_id, leave_type_id=leave_type_id
#             )
        
#         # Filtering leave requests for the given employee, leave type, and within the quarter date range
#         return EmployeeLeavesRequests.objects.filter(
#             employee_id=employee_id,
#             leave_type_id=leave_type_id,
#             start_date__lte=end_date,  
#             end_date__gte=start_date  
#         )
    
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         # Calculate the total number of leave days taken for the given quarter
#         total_leave_days = queryset.aggregate(Sum('leave_days'))['leave_days__sum']
#         total_leave_days = total_leave_days if total_leave_days else 0
        
#         return Response({
#             'quarter': self.request.query_params.get('quarter'),
#             'total_leave_days': total_leave_days,
#             'leave_requests': self.get_serializer(queryset, many=True).data
#         })

class EditLeavePolicyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            leave_policy = LeavePolicyTypes.objects.get(pk=pk)
        except LeavePolicyTypes.DoesNotExist:
            raise NotFound("Leave policy not found.")

        serializer = LeavePolicySerializer(leave_policy)
        return Response(serializer.data, status=200)

    # def put(self, request, pk):
    #     try:
    #         leave_policy = LeavePolicyTypes.objects.get(pk=pk)
    #     except LeavePolicyTypes.DoesNotExist:
    #         raise NotFound("Leave policy not found.")

    #     # Deserialize the incoming data
    #     serializer = LeavePolicySerializer(leave_policy, data=request.data)

    #     if serializer.is_valid():
    #         # Update the LeavePolicyTypes data
    #         updated_leave_policy = serializer.save()

    #         # Update the related LeaveTypeIndex data if necessary
    #         leave_type_data = request.data.get('leave_type')
    #         if leave_type_data:
    #             leave_type = LeaveTypeIndex.objects.get(pk=leave_type_data.get('id'))
    #             leave_type_serializer = LeaveTypeSerializer(leave_type, data=leave_type_data)
    #             if leave_type_serializer.is_valid():
    #                 leave_type_serializer.save()

    #         return Response(serializer.data, status=200)
    #     else:
    #         return Response(serializer.errors, status=400)
    
    # def put(self, request, pk):
    #     try:
    #         leave_policy = LeavePolicyTypes.objects.get(pk=pk)
    #     except LeavePolicyTypes.DoesNotExist:
    #         raise NotFound("Leave policy not found.")

    #     # Deserialize the incoming data
    #     serializer = LeavePolicySerializer(leave_policy, data=request.data)

    #     if serializer.is_valid():
    #         # Update the LeavePolicyTypes data
    #         updated_leave_policy = serializer.save()

    #         # Update the related LeaveTypeIndex data if necessary
    #         leave_type_data = request.data.get('leave_type')
    #         if leave_type_data:
    #             try:
    #                 leave_type = LeaveTypeIndex.objects.get(pk=leave_type_data.get('id'))
    #                 leave_type_serializer = LeaveTypeSerializer(leave_type, data=leave_type_data)
    #                 if leave_type_serializer.is_valid():
    #                     leave_type_serializer.save()
    #             except LeaveTypeIndex.DoesNotExist:
    #                 return Response(
    #                     {"error": "LeaveTypeIndex with the provided ID does not exist."},
    #                     status=400
    #                 )

    #         return Response(serializer.data, status=200)
    #     else:
    #         return Response(serializer.errors, status=400)

from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Case, When, FloatField

class QuarterlyLeaveCalculationView(APIView):
    def get_quarters(self, year):
        return {
            'Q1': (datetime(year, 1, 1), datetime(year, 3, 31)),
            'Q2': (datetime(year, 4, 1), datetime(year, 6, 30)),
            'Q3': (datetime(year, 7, 1), datetime(year, 9, 30)),
            'Q4': (datetime(year, 10, 1), datetime(year, 12, 31)),
        }

    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year', datetime.now().year)  # Get year from query params
        employee_id = kwargs.get('employee_id')
        
        if not employee_id:
            return Response({"error": "Employee ID is required."}, status=400)

        # Fetch leave policies and process as usual
        leave_types = LeavePolicyTypes.objects.all()
        if not leave_types.exists():
            return Response({"error": "No leave policies found."}, status=404)

        quarters = self.get_quarters(int(year))  # Pass the year
        response_data = []

        for leave_policy in leave_types:
            leave_type_index = leave_policy.leave_type
            max_leave_days = leave_policy.max_days * (12 if leave_policy.carry_forward_type == 'monthly' else 4 if leave_policy.carry_forward_type == 'quarterly' else 1)
            quarterly_data = {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0}
            total_booked_days = 0

            for quarter, (start_date, end_date) in quarters.items():
                leaves_in_quarter = EmployeeLeavesRequestsDates.objects.filter(
                    employee__employee__id=employee_id,
                    employee__leave_type=leave_type_index,
                    date__gte=start_date,
                    date__lte=end_date,
                    employee__status_of_leave__in=['Pending', 'Approved']
                )
                leave_days = leaves_in_quarter.aggregate(
                    total_days=Sum(
                        Case(
                            When(leave_day_type='Full day', then=1),
                            When(leave_day_type__startswith='Half day', then=0.5),
                            default=0,
                            output_field=FloatField()
                        )
                    )
                )['total_days'] or 0

                quarterly_data[quarter] = leave_days
                total_booked_days += leave_days

            response_data.append({
                "leave_type": leave_type_index.leavename,
                "quarterly_booked_leaves": quarterly_data,
                "max_leave_days": max_leave_days,
                "total_booked_days": total_booked_days,
                "remaining_leave_days": max_leave_days - total_booked_days
            })

        return Response(response_data)


class YearlyLeaveCalculationView(APIView):
    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year', datetime.now().year)  # Default to the current year
        employee_id = kwargs.get('employee_id')

        if not employee_id:
            return Response({"error": "Employee ID is required."}, status=400)

        # Fetch leave policies
        leave_types = LeavePolicyTypes.objects.all()
        if not leave_types.exists():
            return Response({"error": "No leave policies found."}, status=400)

        response_data = []

        for leave_policy in leave_types:
            leave_type_index = leave_policy.leave_type
            max_leave_days = leave_policy.max_days * (
                12 if leave_policy.carry_forward_type == 'monthly'
                else 4 if leave_policy.carry_forward_type == 'quarterly'
                else 1
            )
            total_booked_days = 0

            # Filter leave requests for the year
            start_date = datetime(int(year), 1, 1)
            end_date = datetime(int(year), 12, 31)
            leaves_in_year = EmployeeLeavesRequestsDates.objects.filter(
                employee__employee__id=employee_id,
                employee__leave_type=leave_type_index,
                date__gte=start_date,
                date__lte=end_date,
                employee__status_of_leave__in=['Pending', 'Approved',]
            )

            # Calculate leave days
            leave_days = leaves_in_year.aggregate(
                total_days=Sum(
                    Case(
                        When(leave_day_type='Full day', then=1),
                        When(leave_day_type__startswith='Half day', then=0.5),
                        default=0,
                        output_field=FloatField()
                    )
                )
            )['total_days'] or 0

            total_booked_days += leave_days

            response_data.append({
                "leave_type": leave_type_index.leavename,
                "total_booked_days": total_booked_days,
                "max_leave_days": max_leave_days,
                "remaining_leave_days": max_leave_days - total_booked_days
            })

        return Response(response_data)


def safe_int(value, default=0):
    """Safely converts a value to integer, returning default if invalid."""
    if value == '':
        return default  # Return None or any suitable default if the value is an empty string.
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

@permission_classes([IsAdmin])
class LeavePolicyTransactionView(APIView):
    def post(self, request):
        try:
            # Start the transaction
            with transaction.atomic():  # Ensure atomic transaction
                data = request.data
                company_id = data.get("company")

                # Safely convert max_days and carry_forward_days to integers
                max_days = safe_int(data.get("max_days", 0))  # Default to 0 if not provided or invalid
                carry_forward_days = safe_int(data.get("carry_forward_days"), 0)  # Default to 0 if not provided or invalid

                # Validate carry forward type and max days
                carry_forward_type = data.get("carry_forward_type", "").lower() 

                if carry_forward_type == 'quarterly' and max_days > 120:
                    return Response({"error": "Maximum days for quarterly carry forward is 120"}, status=400)
                
                if carry_forward_type == 'monthly' and max_days > 30:
                    return Response({"error": "Maximum days for monthly carry forward is 30"}, status=400)

                if carry_forward_days > max_days:
                    return Response({"error": "Carry forward days cannot be greater than maximum days"}, status=400)

                # Step 1: Handle Leave Type Creation or Update
                leave_type_id = data.get("leave_type_id")
                leave_type = None

                if leave_type_id:
                    # Update existing leave type
                    try:
                        leave_type = LeaveTypeIndex.objects.get(id=leave_type_id)
                        leave_type.leavename = data.get("leavename", leave_type.leavename)
                        leave_type.leave_description = data.get("description", leave_type.leave_description)
                        leave_type.save()
                    except LeaveTypeIndex.DoesNotExist:
                        return Response({"error": "Leave Type does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Create new leave type
                    leave_type_data = {
                        "company": company_id,
                        "leavename": data.get("leavename"),
                        "leave_description": data.get("description"),
                    }
                    # Manually create the LeaveTypeIndex instance
                    leave_type = LeaveTypeIndex(
                        company_id=company_id,
                        leavename=leave_type_data["leavename"],
                        leave_description=leave_type_data["leave_description"]
                    )
                    leave_type.save()  # Save to the database

                # Ensure leave_type.id is available after creation
                if not leave_type or not leave_type.id:
                    raise ValueError("Leave Type creation failed. 'leave_type.id' is missing.")

                # Step 2: Handle Leave Policy Creation or Update
                leave_policy_id = data.get("leave_policy_id")
                leave_policy = None

                if leave_policy_id:
                    # Update existing leave policy
                    try:
                        leave_policy = LeavePolicyTypes.objects.get(id=leave_policy_id)
                        leave_policy.max_days = data.get("max_days", leave_policy.max_days)
                        leave_policy.carry_forward_days = data.get("carry_forward_days", leave_policy.carry_forward_days)
                        leave_policy.carry_forward_type = data.get("carry_forward_type", leave_policy.carry_forward_type)
                        leave_policy.carry_forward = data.get("carry_forward", leave_policy.carry_forward)
                        leave_policy.leave_type = leave_type  # Set the foreign key
                        leave_policy.save()
                    except LeavePolicyTypes.DoesNotExist:
                        return Response({"error": "Leave Policy does not exist."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Create new leave policy
                    leave_policy_data = {
                        "leave_type": leave_type.id,  # Pass the leave_type.id explicitly
                        "max_days": data.get("max_days"),
                        "carry_forward_days": data.get("carry_forward_days"),
                        "carry_forward_type": data.get("carry_forward_type"),
                        "carry_forward": data.get("carry_forward"),
                    }
                    # Create the leave policy instance manually
                    leave_policy = LeavePolicyTypes(
                        leave_type=leave_type,
                        max_days=leave_policy_data["max_days"],
                        carry_forward_days=leave_policy_data["carry_forward_days"],
                        carry_forward_type=leave_policy_data["carry_forward_type"],
                        carry_forward=leave_policy_data["carry_forward"]
                    )
                    leave_policy.save()  # Save to the database

                # Ensure leave_policy is valid and has ID
                if not leave_policy or not leave_policy.id:
                    raise ValueError("Leave Policy creation failed. 'leave_policy.id' is missing.")

                # Return a success response with serialized data
                return Response(
                    {
                        "leave_type": LeaveTypeSerializer(leave_type).data,
                        "leave_policy": LeavePolicySerializer(leave_policy).data,
                    },
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            # If an error occurs, rollback the transaction and return an error response
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request):
        """ Handle update for existing Leave Type or Leave Policy """
        try:
            data = request.data
            # Safely convert max_days and carry_forward_days to integers
            max_days = safe_int(data.get("max_days", 0))  # Default to 0 if not provided or invalid
            carry_forward_days = safe_int(data.get("carry_forward_days", 0))  # Default to 0 if not provided or invalid

            # Validate carry forward type and max days
            carry_forward_type = data.get("carry_forward_type", "").lower() 
            if carry_forward_type == 'quarterly' and max_days > 120:
                return Response({"error": "Maximum days for quarterly carry forward is 120"}, status=400)
            
            if carry_forward_type == 'monthly' and max_days > 30:
                return Response({"error": "Maximum days for monthly carry forward is 30"}, status=400)

            if carry_forward_days > max_days:
                return Response({"error": "Carry forward days cannot be greater than maximum days"}, status=400)

            leave_policy_id = data.get("leave_policy_id")
            leave_policy = get_object_or_404(LeavePolicyTypes, id=leave_policy_id)

            # Update leave policy data
            leave_policy.max_days = data.get("max_days", leave_policy.max_days)
            leave_policy.carry_forward_days = data.get("carry_forward_days", leave_policy.carry_forward_days)
            leave_policy.carry_forward_type = data.get("carry_forward_type", leave_policy.carry_forward_type)
            leave_policy.carry_forward = data.get("carry_forward", leave_policy.carry_forward)

            # Update related Leave Type
            leave_type_data = {
                "leavename": data.get("leavename", leave_policy.leave_type.leavename),
                "leave_description": data.get("description", leave_policy.leave_type.leave_description),
            }
            leave_policy.leave_type.leavename = leave_type_data["leavename"]
            leave_policy.leave_type.leave_description = leave_type_data["leave_description"]
            leave_policy.leave_type.save()  # Save the updated leave type

            leave_policy.save()  # Save the updated leave policy

            return Response(
                {
                    "leave_type": LeaveTypeSerializer(leave_policy.leave_type).data,
                    "leave_policy": LeavePolicySerializer(leave_policy).data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            transaction.set_rollback(True)  # Rollback if anything goes wrong
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """ Handle deletion of LeaveTypeIndex and LeavePolicyTypes """
        try:
            # data = request.data
            # print("request", request.data)
            # leave_type_id = data.get("leave_type_id")  # ID of LeaveTypeIndex to delete
            leave_type_id = request.query_params.get('leave_type_id')
            print("id", leave_type_id)

            print("Received Leave Type ID:", leave_type_id)

            if not leave_type_id:
                return Response({"error": "Leave Type ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the LeaveTypeIndex object
            leave_type = get_object_or_404(LeaveTypeIndex, id=leave_type_id)

            # Debug log: Check the leave type being deleted
            print(f"Deleting Leave Type: {leave_type}")

            # Fetch associated leave policies
            leave_policies = LeavePolicyTypes.objects.filter(leave_type=leave_type)

            # Debug log: Check leave policies associated with this leave type
            print(f"Leave Policies to be deleted: {leave_policies}")

            # Deleting associated leave policies
            for policy in leave_policies:
                print(f"Deleting Leave Policy: {policy}")  # Debug log
                policy.delete()

            # Now delete the LeaveTypeIndex
            leave_type.delete()

            return Response(
                {"message": "Leave Type and associated Leave Policies deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            print(f"Error during delete operation: {e}")  # Log error for debugging
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

from datetime import timedelta
from django.db.models import ExpressionWrapper, F, DurationField
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User

class NewHireView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = now()  # Current datetime
        
        # Calculate the days since date_joined for all users
        users = User.objects.annotate(
            days_since_joining=ExpressionWrapper(
                today - F('date_joined'), output_field=DurationField()
            )
        ).values(
            'id', 'username', 'email', 'date_joined', 'role', 'days_since_joining'
        )

        # Filter users who joined this month
        users_this_month = users.filter(
            date_joined__year=today.year,
            date_joined__month=today.month
        )

        # Group results by roles
        roles = {role[0]: role[1] for role in User.ROLE_CHOICES}
        all_users = {}
        new_hires_this_month = {}

        for role_id, role_name in roles.items():
            all_users[role_name] = list(users.filter(role=role_id))
            new_hires_this_month[role_name] = list(users_this_month.filter(role=role_id))

        # Format response
        response = {
            "all_users": all_users,
            "new_hires_this_month": new_hires_this_month
        }
        return Response(response)

