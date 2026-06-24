from rest_framework import serializers
from django.db import transaction
from apps.tickets.services import create_ticket_from_inspection_result
from apps.company.models import Employee, Store
from .models import (
    ChecklistItem,
    ChecklistSection,
    Inspection,
    InspectionItemResult,
)

class ChecklistSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistSection
        fields = (
            "id",
            "name",
            "order",
            "is_active",
        )

class ChecklistItemSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source="section.name", read_only=True)

    class Meta:
        model = ChecklistItem
        fields = (
            "id",
            "section",
            "section_name",
            "title",
            "default_due_days",
            "order",
            "is_active",
        )

class InspectionSerializer(serializers.ModelSerializer):
    store_number = serializers.IntegerField(
        source = "store.store_number",
        read_only = True
    )
    inspector_name = serializers.SerializerMethodField()

    class Meta:
        model = Inspection
        fields = (
            "id",
            "store",
            "store_number",
            "inspector",
            "inspector_name",
            "submitted_at",
        )
        read_only_fields = ("submitted_at",)

    def get_inspector_name(self, obj):
        return f"{obj.inspector.first_name} {obj.inspector.last_name}"
    
class InspectionItemResultSerializer(serializers.ModelSerializer):
    checklist_item_title = serializers.CharField(
        source = "checklist_item.title",
        read_only = True,
    )
    section_name = serializers.CharField(
        source = "checklist_item.section.name",
        read_only = True,
    )

    inspection_store_number = serializers.IntegerField(
        source = "inspection.store.store_number",
        read_only = "True",
    )

    class Meta:
        model = InspectionItemResult
        fields = (
            "id",
            "inspection",
            "inspection_store_number",
            "checklist_item",
            "checklist_item_title",
            "section_name",
            "status",
            "description",
        )

class SubmitInspectionItemResultSerializer(serializers.Serializer):
    checklist_item = serializers.PrimaryKeyRelatedField(
        queryset = ChecklistItem.objects.filter(is_active=True),
    )
    status = serializers.ChoiceField(
        choices = InspectionItemResult.Status.choices,
    )
    description = serializers.CharField(
        required = False,
        allow_blank = True,
    )

    def validate(self, attrs):
        status = attrs["status"]
        description = attrs.get("description", "")

        if status == InspectionItemResult.Status.PROBLEM and not description.strip():
            raise serializers.ValidationError(
                {"description": "Description is required when a problem is found."}
            )
        
        if status == InspectionItemResult.Status.OK and description.strip():
            raise serializers.ValidationError(
                {"description": "Description should be empty when item status is OK."}
            )
        
        return attrs

class SubmitInspectionReportSerializer(serializers.Serializer):
    store = serializers.PrimaryKeyRelatedField(
        queryset = Store.objects.all(),
    )
    results = SubmitInspectionItemResultSerializer(many=True)

    def validate_results(self, results):
        active_item_ids = set(
            ChecklistItem.objects.filter(is_active=True).values_list("id", flat=True)
        )
        submitted_item_ids = {item["checklist_item"].id for item in results}
        missing_item_ids = active_item_ids - submitted_item_ids
        extra_item_ids = submitted_item_ids - active_item_ids

        if missing_item_ids:
            raise serializers.ValidationError(
                f"Missing checklist items: {sorted(missing_item_ids)}"
            )
        
        if extra_item_ids:
            raise serializers.ValidationError(
                f"Invalid checklist items: {sorted(extra_item_ids)}"
            )
        
        if len(submitted_item_ids) != len(results):
            raise serializers.ValidationError(
                "Each checklist item can be submitted only once."
            )
        
        return results
    
    def create(self, validated_data):
        results_data = validated_data.pop("results")

        with transaction.atomic():
            inspection = Inspection.objects.create(**validated_data)

            created_tickets = []

            for result_data in results_data:
                result = InspectionItemResult.objects.create(
                    inspection = inspection,
                    **result_data,
                )

                if result.status == InspectionItemResult.Status.PROBLEM:
                    ticket = create_ticket_from_inspection_result(result)
                    created_tickets.append(ticket)

        return {
            "inspection": inspection,
            "tickets": created_tickets,
        }