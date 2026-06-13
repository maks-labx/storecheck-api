from rest_framework.routers import DefaultRouter

from .views import (
    ChecklistItemViewSet,
    ChecklistSectionViewSet,
    InspectionItemResultViewSet,
    InspectionViewSet,
)

router = DefaultRouter()

router.register("checklist-sections", ChecklistSectionViewSet, basename = "checklist-section")
router.register("checklist-items", ChecklistItemViewSet, basename = "checklist-item")
router.register("inspections", InspectionViewSet, basename = "inspection")
router.register("inspection-results", InspectionItemResultViewSet, basename = "inspection-result")

urlpatterns = router.urls