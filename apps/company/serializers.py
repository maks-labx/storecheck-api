from rest_framework import serializers
from .models import Cluster, Contractor, Employee, Store

class EmployeeSerializer(serializers.ModelSerializer):
    position_display = serializers.CharField(
        source = "get_position_display",
        read_only = True,
    )

    class Meta:
        model = Employee
        fields = (
            "id",
            "employee_number",
            "first_name",
            "last_name",
            "position",
            "position_display",
            "manager",
        )

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = (
            "id",
            "name",
            "cluster_director",
        )

class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contractor
        fields = (
            "id",
            "name",
            "contract_number",
        )

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            "id",
            "store_number",
            "address",
            "cluster",
            "store_director",
            "responsible_engineer",
            "contractor",
        )