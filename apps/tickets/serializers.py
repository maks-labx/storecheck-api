from rest_framework import serializers
from .models import Ticket
from django.utils import timezone
from rest_framework import serializers
from apps.company.models import Store
from rest_framework.exceptions import PermissionDenied

class TicketSerializer(serializers.ModelSerializer):
    store_number = serializers.IntegerField(
        source = "store.store_number",
        read_only = True,
    )
    created_by_name = serializers.SerializerMethodField()
    responsible_engineer_name = serializers.SerializerMethodField()
    contractor_name = serializers.CharField(
        source = "contractor.name",
        read_only = True,
    )
    is_overdue = serializers.BooleanField(read_only = True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "ticket_number",
            "source_result",
            "title",
            "description",
            "store",
            "store_number",
            "created_by",
            "created_by_name",
            "responsible_engineer",
            "responsible_engineer_name",
            "contractor",
            "contractor_name",
            "status",
            "created_at",
            "due_date",
            "is_overdue",
        )
        read_only_fields = (
            "id",
            "ticket_number",
            "source_result",
            "title",
            "description",
            "store",
            "store_number",
            "created_by",
            "created_by_name",
            "responsible_engineer",
            "responsible_engineer_name",
            "contractor",
            "contractor_name",
            "created_at",
            "due_date",
        )

    def get_created_by_name(self, obj):
        return f"{obj.created_by.first_name} {obj.created_by.last_name}"
    
    def get_responsible_engineer_name(self, obj):
        return (
            f"{obj.responsible_engineer.first_name} "
            f"{obj.responsible_engineer.last_name}"
        )

class ManualTicketCreateSerializer(serializers.ModelSerializer):
    store = serializers.PrimaryKeyRelatedField(
        queryset = Store.objects.all()
    )

    class Meta:
        model = Ticket
        fields = (
            "store",
            "title",
            "description",
            "due_date",
        )

    def validate_due_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Due date cannot be in the past."
            )
        
        return value
    
    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        employee = getattr(user, "employee", None)

        if employee is None:
            raise PermissionDenied(
                "User must be linked to an employee."
            )
        
        store = attrs["store"]

        if user.is_staff or user.is_superuser:
            return attrs
        
        if store.store_director_id == employee.id:
            return attrs
        
        raise PermissionDenied(
            "Only the store director or admins can create manual tickets."
        )
    
    def create(self, validated_data):
        created_by = validated_data.pop("created_by")
        store = validated_data["store"]

        return Ticket.objects.create(
            **validated_data,
            created_by = created_by,
            responsible_engineer = store.responsible_engineer,
            contractor = store.contractor,
            status = Ticket.Status.OPEN,
        )