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
