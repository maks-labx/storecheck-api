from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.company.models import Cluster, Contractor, Employee, Store
from apps.inspections.models import (
    ChecklistItem,
    ChecklistSection,
    Inspection,
    InspectionItemResult,
)
from apps.tickets.models import Ticket

class TicketStatusPermissionTests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.engineer_user = User.objects.create_user(
            username="engineer",
            password="testpass123",
        )
        self.store_director_user = User.objects.create_user(
            username="store_director",
            password="testpass123",
        )
        self.other_store_director_user = User.objects.create_user(
            username="other_store_director",
            password="testpass123",
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="testpass123",
            is_staff=True,
        )

        self.engineer = Employee.objects.create(
            user=self.engineer_user,
            employee_number=1001,
            first_name="Mike",
            last_name="Engineer",
            position=Employee.Position.ENGINEER,
        )
        self.store_director = Employee.objects.create(
            user=self.store_director_user,
            employee_number=1002,
            first_name="John",
            last_name="Director",
            position=Employee.Position.STORE_DIRECTOR,
        )
        self.other_store_director = Employee.objects.create(
            user=self.other_store_director_user,
            employee_number=1003,
            first_name="Other",
            last_name="Director",
            position=Employee.Position.STORE_DIRECTOR,
        )
        self.cluster_director = Employee.objects.create(
            employee_number=1004,
            first_name="Cluster",
            last_name="Director",
            position=Employee.Position.CLUSTER_DIRECTOR,
        )

        self.cluster = Cluster.objects.create(
            name="North Cluster",
            cluster_director=self.cluster_director,
        )
        self.contractor = Contractor.objects.create(
            name="FixIt Ltd",
            contract_number="C-001",
        )
        self.store = Store.objects.create(
            store_number=101,
            address="Main Street 1",
            store_director=self.store_director,
            cluster=self.cluster,
            responsible_engineer=self.engineer,
            contractor=self.contractor,
        )

        self.section = ChecklistSection.objects.create(
            name="Sales floor",
            order=1,
        )
        self.item = ChecklistItem.objects.create(
            section=self.section,
            title="Floor",
            default_due_days=3,
        )
        self.inspection = Inspection.objects.create(
            store=self.store,
            inspector=self.engineer,
        )
        self.result = InspectionItemResult.objects.create(
            inspection=self.inspection,
            checklist_item=self.item,
            status=InspectionItemResult.Status.PROBLEM,
            description="Broken floor tiles.",
        )
        self.ticket = Ticket.objects.create(
            source_result=self.result,
            title="Sales floor / Floor",
            description="Broken floor tiles.",
            store=self.store,
            created_by=self.engineer,
            responsible_engineer=self.engineer,
            contractor=self.contractor,
            due_date=timezone.now().date() + timedelta(days=3),
        )
        self.admin_employee = Employee.objects.create(
            user=self.admin_user,
            employee_number=1005,
            first_name="Admin",
            last_name="User",
            position=Employee.Position.CLUSTER_DIRECTOR,
        )

        self.ticket_url = f"/api/tickets/{self.ticket.id}/"

    def test_engineer_cannot_close_ticket(self):
        self.client.force_authenticate(user=self.engineer_user)

        response = self.client.patch(
            self.ticket_url,
            {"status": Ticket.Status.CLOSED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_store_director_can_close_own_store_ticket(self):
        self.client.force_authenticate(user=self.store_director_user)

        response = self.client.patch(
            self.ticket_url,
            {"status": Ticket.Status.CLOSED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.CLOSED)

    def test_other_store_director_cannot_close_ticket(self):
        self.client.force_authenticate(
            user=self.other_store_director_user,
        )

        response = self.client.patch(
            self.ticket_url,
            {"status": Ticket.Status.CLOSED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,)

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.OPEN)

    def test_admin_can_close_ticket(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.patch(
            self.ticket_url,
            {"status": Ticket.Status.CLOSED},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.CLOSED)

    def test_authenticated_user_can_view_ticket(self):
        self.client.force_authenticate(user=self.engineer_user)

        response = self.client.get(self.ticket_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def store_director_can_create_manual_ticket_for_own_store(self):
        self.client.force_authenticate(user=self.store_director_user)

        payload = {
            "store": self.store.id,
            "title": "Broken entrance door",
            "description": "The entrance door does not close properly.",
            "due_date": timezone.now().date() + timedelta(days=3),
        }

        response = self.client.post(
            "/api/tickets/",
            payload,
            format = "json,"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Ticket.objects.count(), 2)

        ticket = Ticket.objects.latest("id")

        self.assertIsNone(ticket.source_result)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.created_by, self.store_director)
        self.assertEqual(ticket.store, self.store)
        self.assertEqual(
            ticket.responsible_engineer,
            self.store.responsible_engineer,
        )
        self.assertEqual(ticket.contractor, self.store.contractor)

    def test_engineer_cannot_create_manual_ticket(self):
        self.client.force_authenticate(user=self.engineer_user)

        payload = {
            "store": self.store.id,
            "title": "Broken entrance door",
            "description": "The entrance door does not close properly.",
            "due_date": timezone.now().date() + timedelta(days=3),
        }

        response = self.client.post(
            "/api/tickets/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Ticket.objects.count(), 1)

    def test_other_store_director_cannot_create_manual_ticket_for_another_store(self):
        self.client.force_authenticate(
            user=self.other_store_director_user,
        )

        payload = {
            "store": self.store.id,
            "title": "Broken entrance door",
            "description": "The entrance door does not close properly.",
            "due_date": timezone.now().date() + timedelta(days=3),
        }

        response = self.client.post(
            "/api/tickets/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(Ticket.objects.count(), 1)

    def test_admin_can_create_manual_ticket(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "store": self.store.id,
            "title": "Broken entrance door",
            "description": "The entrance door does not close properly.",
            "due_date": timezone.now().date() + timedelta(days=3),
        }

        response = self.client.post(
            "/api/tickets/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Ticket.objects.count(), 2)

        ticket = Ticket.objects.latest("id")

        self.assertIsNone(ticket.source_result)
        self.assertEqual(ticket.created_by, self.admin_employee)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)