from rest_framework import serializers
from .models import (
    LeaveTypeIndex,
    Company,
    LeavePolicyTypes,
    EmployeeLeavesRequests,
    Employee,
    EmployeeLeavesRequestsDates,
    UserFile,
    Holidays,
)

class CompanyMainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


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
        fields = ['id', 'max_days', 'carry_forward_type', 'leave_type', 'carry_forward', 'carry_forward_days']


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
class EmployeeLeaveRequestDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeLeavesRequestsDates
        fields = ['id', 'date', 'leave_day_type']


class EmployeeLeaveRequestSerializer(serializers.ModelSerializer):
    # leave_dates = EmployeeLeaveRequestDateSerializer(many=True, read_only=True)
    employee_firstname = serializers.CharField(source='employee.user.first_name', read_only=True)
    employee_lastname = serializers.CharField(source='employee.user.last_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.leavename', read_only=True)
    reporting_manager_name = serializers.CharField(
        source='reporting_manager.username', read_only=True
    )
    leave_dates = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeLeavesRequests
        fields = [
            'id',                # Unique identifier
            'employee',          # Employee foreign key
            'employee_firstname',  
            'employee_lastname',  
            'leave_type',        # Leave type foreign key
            'leave_type_name',   # Leave type name (readable)
            'reporting_manager', # Reporting manager foreign key
            'reporting_manager_name', # Reporting manager username (readable)
            'reason_for_leave',  # Reason for the leave
            'status_of_leave',   # Leave status (Pending, Approved, Rejected)
            'leave_dates',       
        ]
    
    def get_leave_dates(self, obj):
        return obj.employee_leaves_requests_dates.all().values('date')
        



class ReporteeLeaveBalanceSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    employee = serializers.CharField()
    leave_type = serializers.CharField()
    total_allocated = serializers.IntegerField()
    total_taken = serializers.FloatField()  # Float to account for partial days
    remaining_balance = serializers.FloatField()

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holidays
        fields = ['id', 'holiday_name', 'holiday_date']


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTypeIndex
        fields = '__all__'

class LeavePolicySerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(many = False, read_only = True)
    class Meta:
        model = LeavePolicyTypes
        fields = '__all__'

