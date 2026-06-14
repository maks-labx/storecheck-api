from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    ChecklistItemSerializer,
    ChecklistSectionSerializer,
    InspectionItemResultSerializer,
    InspectionSerializer,
    SubmitInspectionReportSerializer,
)

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

    filterset_fields = (
        "is_active",
    )
    search_fields = (
        "name",
    )
    ordering_fields = (
        "order",
        "name",
    )
    ordering = ("order", "name")

class ChecklistItemViewSet(ModelViewSet):
    queryset = ChecklistItem.objects.all()
    serializer_class = ChecklistItemSerializer

    filterset_fields = (
        "section",
        "is_active",
    )
    search_fields = (
        "title",
        "section__name",
    )
    ordering_fields = (
        "section",
        "order",
        "title",
        "default_due_days",
    )
    ordering = ("section__order", "order", "title")

class InspectionViewSet(ReadOnlyModelViewSet):
    queryset = Inspection.objects.select_related(
        "store",
        "inspector",
    )
    serializer_class = InspectionSerializer

    filterset_fields = (
        "store",
        "inspector",
    )
    search_fields = (
        "store__address",
        "store__store_number",
        "inspector__first_name",
        "inspector__last_name",
    )
    ordering_fields = (
        "submitted_at",
        "store",
        "inspector",
    )
    ordering = ("-submitted_at",)

    @action(detail=False, methods=["post"], url_path="submit-report")
    def submit_report(self, request):
        serializer = SubmitInspectionReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {
                "inspection": InspectionSerializer(result["inspection"]).data,
                "tickets_created": len(result["tickets"]),
                "tickets": [
                    {
                        "id": ticket.id,
                        "ticket_number": ticket.ticket_number,
                        "title": ticket.title,
                        "due_date": ticket.due_date,
                    }
                    for ticket in result["tickets"]
                ],
            },
            status = status.HTTP_201_CREATED,
        )

class InspectionItemResultViewSet(ReadOnlyModelViewSet):
    queryset = InspectionItemResult.objects.select_related(
        "inspection",
        "inspection__store",
        "inspection__inspector",
        "checklist_item",
        "checklist_item__section",
    )
    serializer_class = InspectionItemResultSerializer

    filterset_fields = (
        "inspection",
        "status",
        "checklist_item",
        "checklist_item__section",
    )
    search_fields = (
        "description",
        "inspection__store__address",
        "inspection__store__store_number",
        "checklist_item__title",
        "checklist_item__section__name",
    )
    ordering_fields = (
        "inspection",
        "status",
        "checklist_item",
    )