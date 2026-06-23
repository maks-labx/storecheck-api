from rest_framework.permissions import BasePermission

from apps.company.models import Employee

class IsEngineer(BasePermission):
    message = "Only engineers can submit inspection reports."

    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and hasattr(user, "employee")
            and user.employee.position == Employee.Position.ENGINEER
        )