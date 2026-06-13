from rest_framework import serializers
from .models import Ticket

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
