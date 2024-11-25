from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee, LeavePolicyTypes, EmployeeLeavesBalance

@receiver(post_save, sender=Employee)
def create_leave_balance_for_employee(sender, instance, created, **kwargs):
    if created:
        leave_types = LeavePolicyTypes.objects.filter(leave_type__company=instance.company)
        for leave_type in leave_types:
            EmployeeLeavesBalance.objects.create(
                employee=instance,
                leave_type=leave_type,
                total_allocated=leave_type.max_days,
                remaining_balance=leave_type.max_days
            )

@receiver(post_save, sender=LeavePolicyTypes)
def create_leave_balance_for_policy(sender, instance, created, **kwargs):
    if created:
        employees = Employee.objects.filter(company=instance.leave_type.company)
        for employee in employees:
            EmployeeLeavesBalance.objects.create(
                employee=employee,
                leave_type=instance,
                total_allocated=instance.max_days,
                remaining_balance=instance.max_days
            )
