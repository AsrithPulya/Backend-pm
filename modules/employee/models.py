from django.db import models
import string
import random
from django import forms
from modules.account.models import User
from datetime import date
from django.conf import settings
#EMPLOYEE REGISTRATION MODULE
#Company Main Model
class Company(models.Model):
    company_name = models.CharField(max_length=40, unique=True)
    company_gstno = models.CharField(max_length=15, unique=True, null=False)  
    createdby = models.CharField(max_length=40, null=False)  
    created_at = models.DateTimeField(auto_now_add=True)
#Employee Model
class Employee(models.Model):
    company = models.ForeignKey(Company, related_name="employee_company", on_delete=models.CASCADE)
    emp_code = models.CharField(max_length=8) 
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    father_name = models.CharField(max_length=50, null=True, blank=True)
    mother_name = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True) 
    adhaar_number = models.CharField(max_length=12, unique=False, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee")
    pan_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    emergency_number = models.CharField(max_length=10, unique=True, blank=True, null=True)

#Education Types
    def __str__(self):
        return f"{self.company}"


EDUCATION = (
    ('10th class','10TH CLASS'),
    ('12th class', '12TH CLASS'),
    ('b.tech','B.TECH'),
    ('m.tech','M.TECH'),
    ('mca','MCA'),
    ('bca','BCA'),
    )

#Employee Education
class EmployeeEducation(models.Model):
    education_type = models.CharField(max_length=20, choices=EDUCATION, default='10th class')
    college_name = models.CharField(max_length=50)
    college_location = models.CharField(max_length=40)
    start_year = models.DateField()
    end_year = models.DateField()
    employee = models.ForeignKey(Employee, related_name="employee_educations", on_delete=models.CASCADE)


#Employee Attachments Model
DOCUMENTS = (
    ('aadhar', 'Aadhar Card'),
    ('pan', 'Pan Card'),
)
class EmployeeAttachments(models.Model):
    employee = models.ForeignKey(Employee, related_name="employee_attachments", on_delete=models.CASCADE)
    document_type = models.CharField(max_length=20, choices=DOCUMENTS, default='aadhar' )
    file_name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)


#UserFiles Model
# class UserFile(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     file = models.FileField(upload_to='user_files/')
#     file_name = models.CharField(max_length=255)
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.file_name}"
    
#LEAVE MANAGEMENT MODULE
#Types of Leaves Model
class LeaveTypeIndex(models.Model):
    leavename = models.CharField(max_length=50, unique=True)
    leave_description = models.TextField(max_length=255)
    company = models.ForeignKey(Company, related_name="leave_types", on_delete=models.CASCADE)
CARRYTYPE = (
    ('monthly','MONTHLY'),
    ('quarterly', 'QUARTERLY'),
)
#Leave Policies Model
class LeavePolicyTypes(models.Model):
    max_days = models.IntegerField()
    carry_forward_type = models.CharField(max_length=10, choices=CARRYTYPE, default='monthly')
    carry_forward = models.BooleanField(default=False)
    leave_type = models.OneToOneField(LeaveTypeIndex, related_name="leave_policy_types", on_delete=models.CASCADE)
    carry_forward_days = models.FloatField(default=0)
LEAVE_STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Rejected', 'Rejected'),
    ('Cancelled', 'Cancelled'),
)
LEAVE_DAY_TYPE = (
    ('Full day', 'Full day'),
    ('Half day (1st half)', 'Half day (1st half)'),
    ('Half day (2nd half)', 'Half day (2nd half)'),
)
#Employee Leave Requests Model
class EmployeeLeavesRequests(models.Model):
    employee = models.ForeignKey(Employee, related_name="employee_leaves_requests", on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveTypeIndex, on_delete=models.CASCADE)
    reporting_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason_for_leave = models.TextField()
    status_of_leave = models.CharField(max_length=10, choices=LEAVE_STATUS, default='Pending')
#Employee Leave Requests Dates Model
class EmployeeLeavesRequestsDates(models.Model):
    employee = models.ForeignKey(EmployeeLeavesRequests, related_name="employee_leaves_requests_dates", on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    # leave_day_type = models.CharField(max_length=20, choices=LEAVE_DAY_TYPE, default='Full day')
    leave_day_type = models.CharField(max_length=50, null=True, choices=LEAVE_DAY_TYPE, default='Full day')
#Holidays Model
class Holidays(models.Model):
    holiday_name = models.CharField(max_length=50)
    holiday_date = models.DateField(default=date.today)







    