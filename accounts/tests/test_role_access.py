from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.doctors.models import DoctorProfile
from apps.hospitals.models import Hospital


User = get_user_model()


class RoleAccessTestCase(APITestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(
            name="City Care Hospital",
            slug="city-care-hospital",
            city="Kathmandu",
            status=Hospital.Status.ACTIVE,
            is_verified=True,
        )

        self.superadmin = User.objects.create_user(
            email="superadmin@example.com",
            password="StrongPass123!",
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
        )

        self.hospital_admin = User.objects.create_user(
            email="hospitaladmin@example.com",
            password="StrongPass123!",
            first_name="Hospital",
            last_name="Admin",
            role="hospital_admin",
            hospital=self.hospital,
        )

        self.doctor = User.objects.create_user(
            email="doctor@example.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Doe",
            role="doctor",
            hospital=self.hospital,
        )
        DoctorProfile.objects.create(user=self.doctor, hospital=self.hospital)

        self.patient = User.objects.create_user(
            email="patient@example.com",
            password="StrongPass123!",
            first_name="Jane",
            last_name="Patient",
            role="patient",
        )

    def _authenticate(self, user):
        self.client.force_authenticate(user=user)

    def _assert_role_endpoint_access(self, url, allowed_user, denied_users, success_assertion=None):
        self._authenticate(allowed_user)
        allowed_response = self.client.get(url)
        self.assertEqual(allowed_response.status_code, status.HTTP_200_OK)
        self.assertTrue(allowed_response.data["success"])
        if success_assertion:
            success_assertion(allowed_response)

        for denied_user in denied_users:
            with self.subTest(endpoint=url, denied_role=denied_user.role):
                self._authenticate(denied_user)
                denied_response = self.client.get(url)
                self.assertEqual(denied_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_superadmin_endpoint_access(self):
        self._assert_role_endpoint_access(
            url=reverse("accounts:admin-stats"),
            allowed_user=self.superadmin,
            denied_users=[self.hospital_admin, self.doctor, self.patient],
        )

    def test_hospital_admin_endpoint_access(self):
        self._assert_role_endpoint_access(
            url=reverse("accounts:hospital-admin-stats"),
            allowed_user=self.hospital_admin,
            denied_users=[self.superadmin, self.doctor, self.patient],
        )

    def test_doctor_endpoint_access(self):
        self._assert_role_endpoint_access(
            url=reverse("doctors:my-availability"),
            allowed_user=self.doctor,
            denied_users=[self.superadmin, self.hospital_admin, self.patient],
            success_assertion=lambda response: self.assertIn("weekly_slots", response.data["data"]),
        )

    def test_patient_endpoint_access(self):
        self._assert_role_endpoint_access(
            url=reverse("patients:my-profile"),
            allowed_user=self.patient,
            denied_users=[self.superadmin, self.hospital_admin, self.doctor],
            success_assertion=lambda response: self.assertEqual(response.data["data"]["user"]["id"], self.patient.id),
        )
