from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.company.models import Contractor

class ReferenceDataPermissionTests(APITestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="regular_user",
            password="testpass123",
        )
        self.admin_user = User.objects.create_user(
            username="admin_user",
            password="testpass123",
            is_staff=True,
        )

        self.contractors_url = "/api/contractors/"

    def test_authenticated_user_can_view_reference_data(self):
        Contractor.objects.create(
            name="Existing Contractor",
            contract_number="C-001",
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.contractors_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_admin_user_cannot_create_reference_data(self):
        self.client.force_authenticate(user=self.user)

        payload = {
            "name": "New contractor",
            "contract_number": "C-002",
        }

        response = self.client.post(
            self.contractors_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Contractor.objects.count(), 0)

    def test_admin_user_can_create_reference_data(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            "name": "New Contractor",
            "contract_number": "C-003",
        }

        response = self.client.post(
            self.contractors_url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Contractor.objects.count(), 1)