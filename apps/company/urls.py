from rest_framework.routers import DefaultRouter
from .views import ClusterViewSet, ContractorViewSet, EmployeeViewSet, StoreViewSet

router = DefaultRouter()

router.register("employees", EmployeeViewSet, basename = "employee")
router.register("clusters", ClusterViewSet, basename = "cluster")
router.register("contractors", ContractorViewSet, basename = "contractor")
router.register("stores", StoreViewSet, basename = "store")

urlpatterns = router.urls