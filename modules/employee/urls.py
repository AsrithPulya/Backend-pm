from django.urls import path,include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf import settings
from django.conf.urls.static import static

def test_view(request):
    return JsonResponse({"message": "URL is working!"})

 
#files upload 
router = DefaultRouter()
# router.register(r'files', UserFileViewSet, basename='userfile')
router.register(r'employees', EmployeeViewSet, basename='employee')

urlpatterns = [
    path('companies/', CompanyListCreateAPIView.as_view(), name='company_list_create'),
    ##My-company GET API
    path('employees/create/', CreateEmployeeView.as_view(), name='create_employee'),
    path('employees/', EmployeeListView.as_view(), name='employee_list'),
    path('employees/me/', CurrentEmployeeView.as_view(), name='current_employee'),
    path('profile-employees/', ProfileView.as_view(), name='employee_profiles'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='update_employee'),
    # Leave Type Management
    path('leave-types/', LeaveTypeListView.as_view(), name='list_leave_types'),
    path('leave-types/create/', LeaveTypeCreateView.as_view(), name='create_leave_type'),
    path('leave-types/<int:pk>/update/', LeaveTypeUpdateView.as_view(), name='update_leave_type'),
    path('leave-types/<int:pk>/delete/', LeaveTypeDeleteView.as_view(), name='delete_leave_type'),
    # Leave Policy Management
    path('leave-policies/', LeavePolicyListView.as_view(), name='list_leave_policies'),
    path('leave-policies/create/', LeavePolicyCreateView.as_view(), name='create_leave_policy'),
    path('leave-policies/<int:pk>/update/', LeavePolicyUpdateView.as_view(), name='update_leave_policy'),
    path('leave-policies/<int:pk>/delete/', LeavePolicyDeleteView.as_view(), name='delete_leave_policy'),
    path('leave-policies/<int:pk>/', EditLeavePolicyView.as_view(), name='edit_leave_policy'),
    # Employee Balance Views
    path('employee/leave-balance/', EmployeeLeaveBalanceView.as_view(), name='employee_leave_balance'),
    path('admin/leave-balances/', AdminLeaveBalancesView.as_view(), name='admin_leave_balances'),
    # Leave Request Management
    path('leave-requests/apply/', ApplyForLeaveView.as_view(), name='apply_for_leave'),
    path('leave-requests/', EmployeeLeaveRequestsView.as_view(), name='employee_leave_requests'),
    path('leave-requests-cancel/<int:pk>/', EmployeeLeaveRequestsView.as_view(), name='cancel-leave-request'),
    path('admin/leave-requests/', AdminLeaveRequestsView.as_view(), name='admin_leave_requests'),
    path('leave-requests/<int:pk>/', ViewLeaveRequestView.as_view(), name='view_leave_request'),
    path('reportees/', ReporteesListView.as_view(), name='reportees_list'),
    path('reportees/leave-requests/', ReporteesLeaveRequestsView.as_view(), name='reportees_leave_requests'),
    path('reportees/leave-balances/', ReporteesLeaveBalanceView.as_view(), name='reportees_leave_balances'),
    path('leave-requests/<int:pk>/update-status/', UpdateLeaveRequestStatusView.as_view(), name='update_leave_request_status'),
    path('leave-requests/<int:leave_id>/approve-reject/', ApproveRejectLeaveRequest.as_view(), name='approve_reject_leave_request'),
    # Reset Leaves
    path('reset-leave-balances/', reset_leave_balances, name='reset_leave_balances'),
    path('test-reset-leave-balances/', TestResetLeaveBalanceView.as_view(), name='test_reset_leave_balances'),
    #Holidays
    path('holidays/', HolidayListView.as_view(), name='holiday_list'),
    path('holidays/<int:pk>/', HolidayDetailView.as_view(), name='holiday_detail'),

    path('leave-policies/transaction/', LeavePolicyTransactionView.as_view(), name="leave_policies_transaction"),
    path('update_leave_policy/', LeavePolicyTransactionView.as_view(), name='update_leave_policy'),
    path('delete_leave_policy/', LeavePolicyTransactionView.as_view(), name='delete_leave_policy'),

    path('quarterly-leaves/<int:employee_id>/', QuarterlyLeaveCalculationView.as_view(), name='quarterly_leaves'),
    # GET /api/yearly-leaves/123/?year=2023
    path('yearly-leaves/<int:employee_id>/', YearlyLeaveCalculationView.as_view(), name='yearly_leave_calculation'),
    path('new-hires/', NewHireView.as_view(), name='new-hires'),
    path('educations/', EmployeeEducationListCreateView.as_view(), name='education-list-create'),
    path('educations/<int:pk>/', EmployeeEducationListCreateView.as_view(), name='education-list'),
    path('employee-attachments/', EmployeeAttachmentAPIListCreateView.as_view(), name='employee-attachments'),
]
