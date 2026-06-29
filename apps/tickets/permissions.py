from rest_framework.permissions import BasePermission, SAFE_METHODS

class CanUpdateTicketsStatus(BasePermission):
    message = "Only the store director or admins can update ticket status."

    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        user = request.user

        if user.is_staff or user.is_superuser:
            return True
        
        employee = getattr(user, "employee", None)

        return (
            employee is not None
            and obj.store.store_director_id == employee.id
        )