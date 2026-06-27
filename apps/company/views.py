from rest_framework.viewsets import ModelViewSet
from .models import Cluster, Contractor, Employee, Store
from .serializers import (
    ClusterSerializer,
    ContractorSerializer,
    EmployeeSerializer,
    StoreSerializer
)
from apps.common.permissions import IsAdminOrAuthenticatedReadOnly

class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]

    filterset_fields = (
        "position",
        "manager",
    )
    search_fields = (
        "first_name",
        "last_name",
        "employee_number",
    )
    ordering_fields = (
        "employee_number",
        "last_name",
        "position",
    )
    ordering = ("employee_number",)

class ClusterViewSet(ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]

    search_fields = (
        "name",
    )
    ordering_fields = (
        "name",
    )
    ordering = ("name",)

class ContractorViewSet(ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]

    search_fields = (
        "name",
        "contract_number",
    )
    ordering_fields = (
        "name",
        "contract_number",
    )
    ordering = ("name",)

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAdminOrAuthenticatedReadOnly]

    filterset_fields = (
        "cluster",
        "contractor",
        "responsible_engineer",
        "store_director",
    )
    search_fields = (
        "store_number",
        "address",
        "cluster__name",
        "contractor__name",
    )
    ordering_fields = (
        "store_number",
        "address",
    )
    ordering = ("store_number",)