from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_number",
        "title",
        "store",
        "created_by",
        "responsible_engineer",
        "contractor",
        "status",
        "due_date",
        "is_overdue",
        "created_at",
    )
    search_fields = (
        "=ticket_number",
        "title",
        "description",
        "=store__store_number",
        "store__address",
        "created_by__first_name",
        "created_by__last_name",
        "responsible_engineer__first_name",
        "responsible_engineer__last_name",
        "contractor__name",
    )
    list_filter = (
        "status",
        "store__cluster",
        "contractor",
        "responsible_engineer",
        "due_date",
        "created_at",
    )
    readonly_fields = (
        "ticket_number",
        "created_at",
        "is_overdue",
    )
    date_hierarchy = "created_at"
    
