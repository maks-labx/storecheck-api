from django.contrib import admin
from .models import Employee, Cluster, Contractor, Store

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_number", "first_name", "last_name", "position", "user", "manager")
    search_fields = ("=employee_number", "first_name", "last_name", "user__username", "user__email",)
    list_filter = ("position",)

@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ("name", "cluster_director")
    search_fields = ("name",)

@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ("name", "contract_number")
    search_fields = ("name", "contract_number")

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "store_number",
        "address",
        "cluster",
        "store_director",
        "responsible_engineer",
        "contractor",
    )
    search_fields = ("=store_number", "address")
    list_filter = ("cluster", "contractor")
