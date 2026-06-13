from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import (
    ChecklistItem,
    ChecklistSection,
    Inspection,
    InspectionItemResult,
)
from .serializers import (
    ChecklistItemSerializer,
    ChecklistSectionSerializer,
    InspectionItemResultSerializer,
    InspectionSerializer,
)

class ChecklistSectionViewSet(ModelViewSet):
    queryset = ChecklistSection.objects.all()
    serializer_class = ChecklistSectionSerializer

class ChecklistItemViewSet(ModelViewSet):
    queryset = ChecklistItem.objects.all()
    serializer_class = ChecklistItemSerializer

class InspectionViewSet(ReadOnlyModelViewSet):
    queryset = Inspection.objects.select_related(
        "store",
        "inspector",
    )
    serializer_class = InspectionSerializer

class InspectionItemResultViewSet(ReadOnlyModelViewSet):
    queryset = InspectionItemResult.objects.select_related(
        "inspection",
        "inspection__store",
        "inspection__inspector",
        "checklist_item",
        "checklist_item__section",
    )
    serializer_class = InspectionItemResultSerializer
