#IMPORTS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib import messages
from datetime import date
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee
from .serializers import LeaveTypeIndexSerializer, LeavePolicyTypesSerializer, EmployeeLeaveRequestSerializer, CompanyMainSerializer, EmployeeSerializer, EmployeeLeavesRequests, ReporteeLeaveBalanceSerializer
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

#Adding a Company
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
            return Response({'message': 'Leave policy created successfully.'}, status=status.HTTP_201_CREATED)
        
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
        employee = request.user.employee
        leave_balances = []
        leave_types = LeaveTypeIndex.objects.filter(company=employee.company)

        for leave_type in leave_types:
            try:
                # Getting the max days allocated for the leave type
                leave_policy = LeavePolicyTypes.objects.get(leave_type=leave_type)
                max_days = leave_policy.max_days
            except LeavePolicyTypes.DoesNotExist:
                max_days = 0

            # Getting all existing approved or pending leave requests for the employee and leave type
            existing_leave_requests = EmployeeLeavesRequests.objects.filter(
                employee_id=employee,
                leave_type=leave_type,
                status_of_leave__in=['Approved', 'Pending']
            )

            # Calculate the total business days for existing leave requests
            total_existing_days = sum(
                count_business_days(leave_request.start_date, leave_request.end_date)
                for leave_request in existing_leave_requests
            )

            # If carry_forward is allowed, include it in the calculation
            if leave_policy.carry_forward:
                remaining_days = max(0, max_days - total_existing_days)
                carry_forward_limit = 20 #leave_policy.carry_forward_limit  # field for max carry-forward
                carried_forward_days = min(remaining_days, carry_forward_limit) if carry_forward_limit else remaining_days
                remaining_balance = max(0, max_days - total_existing_days + carried_forward_days)
            else:
                # No carry-forward logic; calculate normally
                remaining_balance = max(0, max_days - total_existing_days)

            # Add leave balance information to the response
            leave_balances.append({
                'leave_type': leave_type.leavename,
                'total_allocated': max_days,
                'total_taken': total_existing_days,
                'remaining_balance': remaining_balance
            })

        # Return the response with the leave balances
        return Response(leave_balances, status=status.HTTP_200_OK)

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

class ApplyForLeaveView(APIView):
    def post(self, request):
        # Extract data from the request
        employee = request.data.get('employee')
        leave_type_id = request.data.get('leave_type')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        leave_day_type = request.data.get('leave_day_type')
        reporting_manager = request.data.get('reporting_manager')
        reason_for_leave = request.data.get('reason_for_leave')

        # Validate required fields
        if not all([employee, leave_type_id, start_date, end_date, reason_for_leave]):
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert date strings to date objects
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if start_date is after end_date
        if start_date > end_date:
            return Response({"error": "End date cannot be before start date."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate business days for the new leave request
        total_days_requested = count_business_days(start_date, end_date)
        print(f"Total business days requested between {start_date} and {end_date}: {total_days_requested}")

        # Retrieve the leave type and related leave policy (Error Handling)
        try:
            leave_type = LeaveTypeIndex.objects.get(id=leave_type_id)
        except LeaveTypeIndex.DoesNotExist:
            return Response({"error": "Invalid leave type."}, status=status.HTTP_400_BAD_REQUEST)

        leave_policy_type = LeavePolicyTypes.objects.filter(leave_type=leave_type).first()
        if not leave_policy_type:
            return Response(
                {"error": f"No leave policy found for the leave type '{leave_type.leavename}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        max_days = leave_policy_type.max_days

        # Check if the new request exceeds the max_days allowed
        if total_days_requested > max_days:
            return Response(
                {"error": f"You can only apply for a maximum of {max_days} business days for {leave_type.leavename} leave."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get all existing approved or pending leave requests for the employee and specific leave type
        existing_leave_requests = EmployeeLeavesRequests.objects.filter(
            employee_id=employee,
            leave_type=leave_type,
            status_of_leave__in=['Approved', 'Pending']
        )

        # Calculate total business days for existing leave requests
        total_existing_days = 0
        for leave_request in existing_leave_requests:
            days = count_business_days(leave_request.start_date, leave_request.end_date)
            total_existing_days += days
            print(f"Existing leave request from {leave_request.start_date} to {leave_request.end_date}: {days} days")

        print(f"Total existing business days for leave type '{leave_type.leavename}': {total_existing_days}")

        # Check if the new request plus existing leave days exceed the max_days
        if total_existing_days + total_days_requested > max_days:
            return Response(
                {"error": f"Total leave days for {leave_type.leavename} cannot exceed {max_days} business days."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the leave request if all the conditions are satisfied
        leave_request = EmployeeLeavesRequests.objects.create(
            employee_id=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            leave_day_type=leave_day_type,
            reporting_manager_id=reporting_manager,
            reason_for_leave=reason_for_leave,
            status_of_leave='Pending'
        )

        return Response(
            {"message": "Leave request submitted successfully.", "leave_request_id": leave_request.id},
            status=status.HTTP_201_CREATED
        )

# View for Employee to see the leave his specifically
class EmployeeLeaveRequestsView(APIView):
    def get(self, request):
        leave_requests = EmployeeLeavesRequests.objects.filter(employee=request.user.employee)
        serializer = EmployeeLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReporteesLeaveRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the logged-in user's reportees' leave requests
        reportees = request.user.reportees.all()  # Get the reportees of the logged-in user
        leave_requests = EmployeeLeavesRequests.objects.filter(employee__user__in=reportees)

        serializer = EmployeeLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data)

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

class ApproveRejectLeaveRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, leave_id):
        action = request.data.get("action")
        try:
            leave_request = EmployeeLeavesRequests.objects.get(id=leave_id)
        except EmployeeLeavesRequests.DoesNotExist:
            return Response({"error": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Debugging
        print(f"Request user ID: {request.user.id if request.user else 'None'}")
        print(f"Leave request reporting manager ID: {leave_request.reporting_manager.id if leave_request.reporting_manager else 'None'}")

        # Check if the logged-in user is the reporting manager
        if request.user.id != leave_request.reporting_manager.id:
            return Response({"error": "You are not authorized to approve or reject this leave request."}, status=status.HTTP_403_FORBIDDEN)

        # Update the status of the leave request
        if action == "approve":
            leave_request.status_of_leave = "Approved"
        elif action == "reject":
            leave_request.status_of_leave = "Rejected"
        else:
            return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

        leave_request.save()
        return Response({"message": f"Leave request {action}d successfully."}, status=status.HTTP_200_OK)

class ReporteesListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reporting_manager = request.user
        reportees = Employee.objects.filter(user__reporting_manager=reporting_manager)
        serializer = EmployeeSerializer(reportees, many=True)
        return Response(serializer.data)
    

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
            # Simulate the reset leave logic manually 
            current_date = datetime.now().date()
            if current_date.day >= 1:  
                employees = Employee.objects.all()

                for employee in employees:
                    leave_types = LeaveTypeIndex.objects.filter(company=employee.company)

                    for leave_type in leave_types:
                        try:
                            policy = LeavePolicyTypes.objects.get(leave_type=leave_type)
                        except LeavePolicyTypes.DoesNotExist:
                            policy = None
                            continue

                        if policy and (policy.carry_forward_type == 'monthly' or (policy.carry_forward_type == 'quarterly' and current_date.month in [1, 4, 7, 10])):
                            
                            # Calculate the total approved leaves taken for the employee and leave type
                            total_approved_days = EmployeeLeavesRequests.objects.filter(
                                leave_type=leave_type,
                                employee=employee,
                                status_of_leave='Approved'
                            ).count()

                            # Calculate remaining balance based on policy
                            if policy.carry_forward:
                                remaining_balance = max(0, policy.max_days - total_approved_days)
                            else:
                                remaining_balance = policy.max_days

                            # Optionally, reset the leave taken count
                            EmployeeLeavesRequests.objects.filter(employee=employee, leave_type=leave_type, status_of_leave='Approved').delete()

                            # Print the result for each employee and leave type (for testing purposes)
                            print(f"Leave balance reset for {employee.user.first_name} {employee.user.last_name} for {leave_type.leavename} - Remaining Balance: {remaining_balance}")
            
            return Response({"message": "Leave balances manually reset triggered."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ReporteesLeaveBalanceView(APIView):
    def get(self, request):
        leave_balances = []
        
        # Adjusted filtering to access the 'reporting_manager' via 'user'
        reportees = Employee.objects.filter(user__reporting_manager=request.user)

        for reportee in reportees:
            leave_types = LeaveTypeIndex.objects.filter(company=reportee.company)

            for leave_type in leave_types:
                try:
                    leave_policy = LeavePolicyTypes.objects.get(leave_type=leave_type)
                    max_days = leave_policy.max_days
                except LeavePolicyTypes.DoesNotExist:
                    max_days = 0

                existing_leave_requests = EmployeeLeavesRequests.objects.filter(
                    employee=reportee,
                    leave_type=leave_type,
                    status_of_leave__in=['Approved', 'Pending']
                )

                total_existing_days = sum(
                    count_business_days(leave_request.start_date, leave_request.end_date)
                    for leave_request in existing_leave_requests
                )

                if leave_policy.carry_forward:
                    remaining_days = max(0, max_days - total_existing_days)
                    carry_forward_limit = 20  # Adjust if needed
                    carried_forward_days = min(remaining_days, carry_forward_limit) if carry_forward_limit else remaining_days
                    remaining_balance = max(0, max_days - total_existing_days + carried_forward_days)
                else:
                    remaining_balance = max(0, max_days - total_existing_days)

                # Check if the employee is on leave today
                today = timezone.now().date()
                on_leave_today = EmployeeLeavesRequests.objects.filter(
                    employee=reportee,
                    leave_type=leave_type,
                    start_date__lte=today,
                    end_date__gte=today,
                    status_of_leave='Approved'
                ).exists()

                leave_balances.append({
                    'reportee_first_name': reportee.user.first_name,
                    'reportee_last_name': reportee.user.last_name,
                    'leave_type': leave_type.leavename,
                    'total_allocated': max_days,
                    'total_taken': total_existing_days,
                    'remaining_balance': remaining_balance,
                    'on_leave_today': on_leave_today  # New field to check if on leave today
                })

        return Response(leave_balances, status=status.HTTP_200_OK)

