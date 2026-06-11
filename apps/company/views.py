from rest_framework.viewsets import ModelViewSet
from .models import Cluster, Contractor, Employee, Store
from .serializers import (
    ClusterSerializer,
    ContractorSerializer,
    EmployeeSerializer,
    StoreSerializer
)

class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ClusterViewSet(ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

class ContractorViewSet(ModelViewSet):
    queryset = Contractor.objects.all()
    serializer_class = ContractorSerializer

class StoreViewSet(ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer