from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.company.models import Cluster, Contractor, Employee, Store
from apps.inspections.models import (
    ChecklistItem,
    ChecklistSection,
    Inspection,
    InspectionItemResult,
)
from apps.tickets.models import Ticket

class SubmitInspectionReportAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username = "testuser",
            password = "testpass123",
        )
        self.client.force_authenticate(user=self.user)

        self.cluster_director = Employee.objects.create(
            employee_number = 1001,
            first_name = "John",
            last_name = "Director",
            position = Employee.Position.CLUSTER_DIRECTOR,
        )
        self.store_director = Employee.objects.create(
            employee_number = 1002,
            first_name = "Sarah",
            last_name = "Store",
            position = Employee.Position.STORE_DIRECTOR,
        )
        self.engineer = Employee.objects.create(
            employee_number = 1003,
            first_name = "Mike",
            last_name = "Engineer",
            position = Employee.Position.ENGINEER,
        )

        self.engineer.user = self.user
        self.engineer.save(update_fields=["user"])

        self.store_director_user = User.objects.create_user(
            username = "store_director",
            password = "testpass123",
        )

        self.store_director.user = self.store_director_user
        self.store_director.save(update_fields=["user"])

        self.cluster = Cluster.objects.create(
            name = "Chicago West",
            cluster_director = self.cluster_director,
        )
        self.contractor = Contractor.objects.create(
            name = "Service Group",
            contract_number = "CNT-001",
        )
        self.store = Store.objects.create(
            store_number = 101,
            address = "123 Main Street, Chicago",
            cluster = self.cluster,
            store_director = self.store_director,
            responsible_engineer = self.engineer,
            contractor = self.contractor,
        )

        self.section = ChecklistSection.objects.create(
            name = "Sales floor",
            order = 1,
            is_active = True,
        )
        self.floor_item = ChecklistItem.objects.create(
            section = self.section,
            title = "Floor",
            default_due_days = 3,
            order = 1,
            is_active = True,
        )
        self.lighting_item = ChecklistItem.objects.create(
            section = self.section,
            title = "Lighting",
            default_due_days = 5,
            order = 2,
            is_active = True,
        )

        self.url = "/api/inspections/submit-report/"

    def test_submit_report_creates_inspection_results_and_ticket(self):
        payload = {
            "store": self.store.id,
            "results": [
                {
                    "checklist_item": self.floor_item.id,
                    "status": InspectionItemResult.Status.PROBLEM,
                    "description": "Broken floor tiles near the entrance.",
                },
                {
                    "checklist_item": self.lighting_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Inspection.objects.count(), 1)
        self.assertEqual(InspectionItemResult.objects.count(), 2)
        self.assertEqual(Ticket.objects.count(), 1)

        inspection = Inspection.objects.get()
        self.assertEqual(inspection.inspector, self.engineer)

        ticket = Ticket.objects.first()

        self.assertEqual(ticket.store, self.store)
        self.assertEqual(ticket.created_by, self.engineer)
        self.assertEqual(ticket.responsible_engineer, self.engineer)
        self.assertEqual(ticket.contractor, self.contractor)
        self.assertEqual(ticket.status, Ticket.Status.NEW)
        self.assertEqual(ticket.description, "Broken floor tiles near the entrance.")
        self.assertIn("Floor", ticket.title)

        self.assertEqual(response.data["tickets_created"], 1)

    def test_problem_without_description_returns_400(self):
        payload = {
            "store": self.store.id,
            "results": [
                {
                    "checklist_item": self.floor_item.id,
                    "status": InspectionItemResult.Status.PROBLEM,
                    "description": "",
                },
                {
                    "checklist_item": self.lighting_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
            ],
        }

        response = self.client.post(self.url, payload, format = "json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Inspection.objects.count(), 0)
        self.assertEqual(InspectionItemResult.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_missing_checklist_item_returns_400(self):
        payload = {
            "store": self.store.id,
            "results": [
                {
                    "checklist_item": self.floor_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Inspection.objects.count(), 0)
        self.assertEqual(InspectionItemResult.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_anonymous_user_cannot_submit_report(self):
        self.client.force_authenticate(user=None)

        payload = {
            "store": self.store.id,
            "results": [
                {
                    "checklist_item": self.floor_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
                {
                    "checklist_item": self.lighting_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
            ],
        }

        response = self.client.post(self.url, payload, format = "json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Inspection.objects.count(), 0)
        self.assertEqual(InspectionItemResult.objects.count(), 0)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_submit_report_creates_multiple_tickets_for_multiple_problems(self):
        payload = {
            "store": self.store.id,
            "results": [
                {
                    "checklist_item": self.floor_item.id,
                    "status": InspectionItemResult.Status.PROBLEM,
                    "description": "Broken floor tiles near the entrance.",
                },
                {
                    "checklist_item": self.lighting_item.id,
                    "status": InspectionItemResult.Status.PROBLEM,
                    "description": "Several lights are not working.",
                },
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Inspection.objects.count(), 1)
        self.assertEqual(InspectionItemResult.objects.count(), 2)
        self.assertEqual(Ticket.objects.count(), 2)

        self.assertEqual(response.data["tickets_created"], 2)
        self.assertEqual(len(response.data["tickets"]), 2)

        ticket_titles = list(Ticket.objects.values_list("title", flat=True))
        ticket_descriptions = list(Ticket.objects.values_list("description", flat=True))

        self.assertTrue(any("Floor" in title for title in ticket_titles))
        self.assertTrue(any("Lighting" in title for title in ticket_titles))

        self.assertIn("Broken floor tiles near the entrance.", ticket_descriptions)
        self.assertIn("Several lights are not working.", ticket_descriptions)

    def test_store_director_cannot_submit_report(self):
        self.client.force_authenticate(user=self.store_director_user)

        payload = {
            "store": self.store.id,
            "results": [
                {
                    "checklist_item": self.floor_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
                {
                    "checklist_item": self.lighting_item.id,
                    "status": InspectionItemResult.Status.OK,
                    "description": "",
                },
            ],
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Inspection.objects.count(), 0)

    def test_anonymous_user_cannot_view_stores(self):
        self.client.force_authenticate(user = None)

        response = self.client.get("/api/stores/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_view_stores(self):
        self.client.force_authenticate(user = self.user)

        response = self.client.get("/api/stores/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )