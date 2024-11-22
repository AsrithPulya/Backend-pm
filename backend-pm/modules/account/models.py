from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [
        (1, 'Admin'),
        (2, 'Employee'),
        (3, 'Manager'),
    ]
    email = models.EmailField(unique=True)
    role = models.IntegerField(choices=ROLE_CHOICES, default=2)
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reportees')
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
