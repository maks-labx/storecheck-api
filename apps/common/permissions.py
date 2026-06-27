from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrAuthenticatedReadOnly(BasePermission):
    message = "Only admins can modify reference data."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False
        
        if request.method in SAFE_METHODS:
            return True
        
        return user.is_staff or user.is_superuser