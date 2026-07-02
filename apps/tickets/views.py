from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from .models import Ticket
from .serializers import TicketSerializer, ManualTicketCreateSerializer
from .permissions import CanUpdateTicketsStatus
from rest_framework.response import Response

class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
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
    permission_classes = [CanUpdateTicketsStatus]
    http_method_names = ["get", "post", "patch", "head", "options"]

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

    def get_serializer_class(self):
        if self.action == "create":
            return ManualTicketCreateSerializer
        
        return TicketSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = serializer.save(
            created_by = request.user.employee,
        )

        output_serializer = TicketSerializer(
            ticket,
            context = self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
