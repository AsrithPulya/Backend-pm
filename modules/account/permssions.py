from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 1:
            return True
        return False

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 3:
            return True
        return False

class IsEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role == 2:
            return True
        return False
    
class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.role == 1 or request.user.role == 3)  # 1 = Admin, 3 = Manager
        )
