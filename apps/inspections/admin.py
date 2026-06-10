from django.contrib import admin
from .models import ChecklistSection, ChecklistItem, Inspection, InspectionItemResult

@admin.register(ChecklistSection)
class ChecklistSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)

@admin.register(ChecklistItem)
class CheckListItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "section",
        "default_due_days",
        "order",
        "is_active",
    )
    search_fields = ("title", "section__name")
    list_filter = ("section", "is_active")

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "store",
        "inspector",
        "submitted_at",
    )
    search_fields = (
        "=id",
        "store__store_number",
        "store__address",
        "inspector__first_name",
        "inspector__last_name",
        "inspector__employee_number",
    )
    list_filter = (
        "store__cluster",
        "inspector",
        "submitted_at",
    )
    date_hierarchy = "submitted_at"

@admin.register(InspectionItemResult)
class InspectionItemResultAdmin(admin.ModelAdmin):
    list_display = (
        "inspection",
        "checklist_item",
        "status",
        "short_description",
    )
    search_fields = (
        "inspection__store__store_number",
        "inspection__store__address",
        "checklist_item__title",
        "checklist_item__section__name",
        "description",
    )
    list_filter = (
        "status",
        "checklist_item__section",
        "inspection__store__cluster",
    )
    ordering = (
        "inspection",
        "checklist_item__section__order",
        "checklist_item__order",
    )

    @admin.display(description="Description")
    def short_description(self, obj):
        if not obj.description:
            return "-"
        return obj.description[:60]
