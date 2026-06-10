from datetime import timedelta
from django.utils import timezone
from apps.inspections.models import InspectionItemResult
from .models import Ticket

def create_ticket_from_inspection_result(result: InspectionItemResult) -> Ticket:
    if result.status != InspectionItemResult.Status.PROBLEM:
        raise ValueError("Ticket can be created only from a problem inspection result.")
    
    if hasattr(result, "ticket"):
        return result.ticket
    
    return Ticket.objects.create(
        source_result = result,
        title = f"{result.checklist_item.section.name} / {result.checklist_item.title}",
        description = result.description,
        store = result.inspection.store,
        created_by = result.inspection.inspector,
        responsible_engineer = result.inspection.store.responsible_engineer,
        contractor = result.inspection.store.contractor,
        due_date = timezone.now().date()
        + timedelta(days=result.checklist_item.default_due_days),
    )