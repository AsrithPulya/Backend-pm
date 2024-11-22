from rest_framework import serializers
from .models import LeaveTypeIndex, Company, LeavePolicyTypes, EmployeeLeavesRequests, Employee
from .models import Company, Employee
from .models import UserFile

class CompanyMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'company_gstno', 'createdby', 'created_at']

class EmployeeSerializer(serializers.ModelSerializer):
    Name = serializers.SerializerMethodField() 
    class Meta:
        model = Employee
        fields = ['id', 'company', 'emp_code', 'date_of_birth', 'father_name', 'mother_name', 'phone_number', 'adhaar_number', 'user', 'Name']
        read_only_fields = ["emp_code"]

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


class ProfileSerializer(serializers.ModelSerializer):
    Email = serializers.SerializerMethodField()
    Role = serializers.SerializerMethodField()
    Name = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    class Meta:
        model = Employee 
        fields = ['emp_code', 'Name', 'Email', 'date_of_birth', 'phone_number', 'date_joined' , 'Role']
    def get_Name(self,obj):
        if obj.user:
            return f"{obj.user.first_name}"
        return None
    
    def get_date_joined(self,obj):
        if obj.user:
            return f"{obj.user.date_joined}"
        return None
    def get_Email(self,obj):
        if obj.user:
            return f"{obj.user.email}"
        return None
    
    def get_Role(self, obj):
        if obj.user:
            return f"{obj.user.role}"
        return None

class UserFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ['id', 'user', 'file', 'file_name', 'uploaded_at']
        read_only_fields = ['user']

class UserProfileSerializer(serializers.ModelSerializer):
    Emp_id = serializers.CharField(source='emp_code', read_only=True)
    Name = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    Role = serializers.SerializerMethodField()
    FatherName = serializers.CharField(source='father_name')
    MotherName = serializers.CharField(source='mother_name')
    PersonalMobileNumber = serializers.CharField(source='phone_number')
    user = serializers.SerializerMethodField()


    class Meta:
        model = Employee
        fields = ['id', 'Emp_id', 'Name', 'date_joined', 'Role', 'FatherName', 'MotherName', 'PersonalMobileNumber', 'user']

    def get_Name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else None

    def get_date_joined(self, obj):
        return obj.user.date_joined if obj.user else None

    def get_Role(self, obj):
        return obj.user.role if hasattr(obj.user, 'role') else None
    def get_user(self, obj):
        return obj.user.id


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


