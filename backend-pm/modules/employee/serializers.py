from rest_framework import serializers
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee, Company

class CompanyMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'company_gstno', 'createdby', 'created_at']

class EmployeeSerializer(serializers.ModelSerializer):
    Name = serializers.SerializerMethodField() 
    class Meta:
        model = Employee
        fields = ['id', 'company', 'emp_code', 'date_of_birth', 'father_name', 'mother_name', 'phone_number', 'adhaar_number', 'user', 'Name']

    def get_Name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None 
      
class LeaveTypeIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypeIndex
        fields = ['id', 'leavename', 'leave_description', 'company']

class LeavePolicyTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeavePolicyTypes
        fields = ['id', 'max_days', 'carry_forward_type', 'leave_type', 'carry_forward']

class EmployeeLeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer() 
    leave_type_name = serializers.CharField(source='leave_type.leavename')  
    class Meta:
        model = EmployeeLeavesRequests
        fields = [
            'id', 'employee', 'leave_type', 'leave_type_name', 'start_date', 'end_date', 
            'leave_day_type', 'reporting_manager', 'reason_for_leave', 'status_of_leave'
        ]

class ReporteeLeaveBalanceSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    employee = serializers.CharField()
    leave_type = serializers.CharField()
    total_allocated = serializers.IntegerField()
    total_taken = serializers.FloatField()  # Float to account for partial days
    remaining_balance = serializers.FloatField()







#How to pull data from other tables with Serializers EXAMPLE FOR REFERENCE
# class EmployeeSerializer(serializers.ModelSerializer):
#     Name = serializers.SerializerMethodField() 
#     Email_ID = serializers.SerializerMethodField() 
#     class Meta:
#         model = Employee
#         fields = ['id', 'company', 'emp_code', 'date_of_birth', 'father_name', 'mother_name', 'phone_number', 'adhaar_number', 'user', 'Name']

#     def get_Name(self, obj):
#         if obj.user:
#             return f"{obj.user.first_name} {obj.user.last_name}"
#         return None 
#     def get_Email_ID(self, obj):
#         if obj.user:
#             return f"{obj.user.email}"
#         return None


