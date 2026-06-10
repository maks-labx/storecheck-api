from django.db import models
from django.core.exceptions import ValidationError

from apps.company.models import Employee, Store

class ChecklistSection(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return self.name
    
class ChecklistItem(models.Model):
    section = models.ForeignKey(
        ChecklistSection,
        on_delete=models.PROTECT,
        related_name="items",
    )
    title = models.CharField(max_length=150)
    default_due_days = models.PositiveSmallIntegerField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("section__order", "order", "title")
        unique_together = ("section", "title")

    def __str__(self):
        return f"{self.section} / {self.title}"
    
class Inspection(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        related_name="inspections",
    )
    inspector = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="inspections",
        limit_choices_to={"position": Employee.Position.ENGINEER},
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-submitted_at",)

    def __str__(self):
        return f"Inspection #{self.id} - Store #{self.store.store_number}"
    
class InspectionItemResult(models.Model):
    class Status(models.TextChoices):
        OK = "ok", "OK"
        PROBLEM = "problem", "Problem"

    inspection = models.ForeignKey(
        Inspection,
        on_delete=models.CASCADE,
        related_name="results",
    )
    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.PROTECT,
        related_name="inspection_results",
    )
    status = models.CharField(max_length=20, choices=Status.choices)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("inspection", "checklist_item")
        ordering = ("checklist_item__section__order", "checklist_item__order")

    def clean(self):
        if self.status == self.Status.PROBLEM and not self.description.strip():
            raise ValidationError(
                {"description": "Description is required when a problem is found."}
            )
        
        if self.status == self.Status.OK and self.description.strip():
            raise ValidationError(
                {"description": "Description should be empty when item status is OK."}
            )
        
    def __str__(self):
        return f"{self.inspection} / {self.checklist_item} / {self.status}"
