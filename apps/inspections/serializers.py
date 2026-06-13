from rest_framework import serializers
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
