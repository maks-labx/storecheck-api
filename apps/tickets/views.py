from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from .models import Ticket
from .serializers import TicketSerializer

class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Ticket.objects.select_related(
        "source_result",
        "store",
        "created_by",
        "responsible_engineer",
        "contractor",
    )
    serializer_class = TicketSerializer
    http_method_names = ["get", "patch", "head", "options"]

    filterset_fields = (
        "status",
        "store",
        "contractor",
        "responsible_engineer",
        "created_by",
    )
    search_fields = (
        "ticket_number",
        "title",
        "description",
        "store__address",
        "contractor__name",
        "responsible_engineer__first_name",
        "responsible_engineer__last_name",
    )
    ordering_fields = (
        "created_at",
        "due_date",
        "ticket_number",
        "status",
    )
    ordering = ("due_date", "-created_at")
