from django.db import models

class Employee(models.Model):
    class Position(models.TextChoices):
        CLUSTER_DIRECTOR = "cluster_director", "Cluster Director"
        STORE_DIRECTOR = "store_director", "Store Director"
        CHEIF_ENGINEER = "chief_engineer", "Chief Engineer"
        ENGINEER = "engineer", "Engineer"

    employee_number = models.PositiveIntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=30, choices=Position.choices)
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )

    def __str__(self):
        return f"{self.get_position_display()} {self.last_name} {self.first_name}"
    
class Cluster(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cluster_director = models.OneToOneField(
        Employee,
        on_delete=models.PROTECT,
        related_name="managed_cluster",
        limit_choices_to={"position": Employee.Position.CLUSTER_DIRECTOR},
    )

    def __str__(self):
        return self.name
    
class Contractor(models.Model):
    name = models.CharField(max_length=150, unique=True)
    contract_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Store(models.Model):
    store_number = models.PositiveIntegerField(unique=True)
    address = models.CharField(max_length=255)
    cluster = models.ForeignKey(
        Cluster,
        on_delete=models.PROTECT,
        related_name="stores",
    )
    store_director = models.OneToOneField(
        Employee,
        on_delete=models.PROTECT,
        related_name="managed_store",
        limit_choices_to={"position": Employee.Position.STORE_DIRECTOR},
    )
    responsible_engineer = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="engineering_stores",
        limit_choices_to={"position": Employee.Position.ENGINEER},
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.PROTECT,
        related_name="stores",
    )

    def __str__(self):
        return f"Store #{self.store_number}"
