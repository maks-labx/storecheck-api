from django.db import models
from django.utils import timezone

from apps.company.models import Contractor, Employee, Store
from apps.inspections.models import InspectionItemResult

class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    ticket_number = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
    )

    source_result = models.OneToOneField(
        InspectionItemResult,
        on_delete=models.PROTECT,
        related_name="ticket",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name="tickets"
    )
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="created_tickets",
    )
    responsible_engineer = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="assigned_tickets",
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.PROTECT,
        related_name="tickets",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()

    class Meta:
        ordering = ("due_date", "-created_at")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.ticket_number:
            self.ticket_number = f"{self.pk:06d}"
            super().save(update_fields=["ticket_number"])

    @property
    def is_overdue(self):
        return (
            self.status != self.Status.CLOSED
            and timezone.now().date() > self.due_date
        )
    
    def __str__(self):
        return f"Ticket #{self.ticket_number}"
