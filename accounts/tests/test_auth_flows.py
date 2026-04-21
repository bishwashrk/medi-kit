from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.hospitals.models import Hospital


User = get_user_model()


class AuthAndRegistrationFlowTestCase(APITestCase):
    def setUp(self):
        self.password = "StrongPass123!"

        self.hospital = Hospital.objects.create(
            name="MediHub Central",
            slug="medihub-central",
            city="Kathmandu",
            status=Hospital.Status.ACTIVE,
            is_verified=True,
        )

        self.superadmin = User.objects.create_user(
            email="superadmin.flow@example.com",
            password=self.password,
            first_name="Super",
            last_name="Admin",
            role="super_admin",
            is_staff=True,
            is_superuser=True,
        )

        self.hospital_admin = User.objects.create_user(
            email="hospitaladmin.flow@example.com",
            password=self.password,
            first_name="Hospital",
            last_name="Admin",
            role="hospital_admin",
            hospital=self.hospital,
        )

        self.doctor = User.objects.create_user(
            email="doctor.flow@example.com",
            password=self.password,
            first_name="Doctor",
            last_name="User",
            role="doctor",
            hospital=self.hospital,
        )

        self.patient = User.objects.create_user(
            email="patient.flow@example.com",
            password=self.password,
            first_name="Patient",
            last_name="User",
            role="patient",
        )

    def _login_and_get_tokens(self, email, password):
        login_url = reverse("accounts:login")
        response = self.client.post(
            login_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"], response.data["refresh"]

    def _assert_login_status(self, email, password, expected_status):
        login_url = reverse("accounts:login")
        response = self.client.post(
            login_url,
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, expected_status)
        return response

    def test_login_returns_tokens_for_all_roles(self):
        cases = [
            {
                "email": self.superadmin.email,
                "password": self.password,
                "expected_status": status.HTTP_200_OK,
                "expected_role": self.superadmin.role,
            },
            {
                "email": self.hospital_admin.email,
                "password": self.password,
                "expected_status": status.HTTP_200_OK,
                "expected_role": self.hospital_admin.role,
            },
            {
                "email": self.doctor.email,
                "password": self.password,
                "expected_status": status.HTTP_200_OK,
                "expected_role": self.doctor.role,
            },
            {
                "email": self.patient.email,
                "password": self.password,
                "expected_status": status.HTTP_200_OK,
                "expected_role": self.patient.role,
            },
            {
                "email": self.patient.email,
                "password": "WrongPass123!",
                "expected_status": status.HTTP_401_UNAUTHORIZED,
            },
            {
                "email": "unknown@example.com",
                "password": self.password,
                "expected_status": status.HTTP_401_UNAUTHORIZED,
            },
        ]

        for case in cases:
            with self.subTest(email=case["email"], expected_status=case["expected_status"]):
                response = self._assert_login_status(
                    case["email"],
                    case["password"],
                    case["expected_status"],
                )
                if case["expected_status"] == status.HTTP_200_OK:
                    self.assertIn("access", response.data)
                    self.assertIn("refresh", response.data)
                    self.assertEqual(response.data["user"]["role"], case["expected_role"])

    def test_logout_requires_authentication(self):
        logout_url = reverse("accounts:logout")
        response = self.client.post(logout_url, {"refresh": "abc"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_fails_with_invalid_refresh_token(self):
        logout_url = reverse("accounts:logout")
        access, _ = self._login_and_get_tokens(self.patient.email, self.password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client.post(
            logout_url,
            {"refresh": "invalid-token-value"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_token_refresh_fails_with_invalid_refresh_token(self):
        refresh_url = reverse("accounts:token-refresh")
        response = self.client.post(
            refresh_url,
            {"refresh": "invalid-token-value"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_fails_for_blacklisted_token_after_logout(self):
        logout_url = reverse("accounts:logout")
        refresh_url = reverse("accounts:token-refresh")
        access, refresh = self._login_and_get_tokens(self.patient.email, self.password)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_response = self.client.post(logout_url, {"refresh": refresh}, format="json")
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            refresh_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_register_creates_patient_and_tokens(self):
        register_url = reverse("accounts:register")
        payload = {
            "email": "new.patient@example.com",
            "password": "VeryStrongPass123!",
            "password_confirm": "VeryStrongPass123!",
            "first_name": "New",
            "last_name": "Patient",
            "phone": "9800000001",
        }

        response = self.client.post(register_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["user"]["role"], "patient")
        self.assertIn("access", response.data["data"]["tokens"])
        self.assertIn("refresh", response.data["data"]["tokens"])
        self.assertTrue(User.objects.filter(email=payload["email"], role="patient").exists())

    def test_patient_register_negative_cases(self):
        register_url = reverse("accounts:register")
        cases = [
            {
                "name": "duplicate_email",
                "payload": {
                    "email": self.patient.email,
                    "password": "VeryStrongPass123!",
                    "password_confirm": "VeryStrongPass123!",
                    "first_name": "Duplicate",
                    "last_name": "Patient",
                    "phone": "9800000099",
                },
                "expect_password_confirm_error": False,
            },
            {
                "name": "password_mismatch",
                "payload": {
                    "email": "mismatch.patient@example.com",
                    "password": "VeryStrongPass123!",
                    "password_confirm": "DifferentPass123!",
                    "first_name": "Mismatch",
                    "last_name": "Patient",
                    "phone": "9800000100",
                },
                "expect_password_confirm_error": True,
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                response = self.client.post(register_url, case["payload"], format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                if case["expect_password_confirm_error"]:
                    self.assertIn("errors", response.data)
                    self.assertIn("password_confirm", response.data["errors"])

    def test_hospital_registration_request_creates_pending_hospital_and_admin(self):
        request_url = reverse("accounts:register-hospital")
        payload = {
            "hospital_name": "Future Care",
            "hospital_email": "futurecare@example.com",
            "hospital_phone": "9800000002",
            "address": "Baneshwor",
            "city": "Kathmandu",
            "description": "New hospital request",
            "admin_first_name": "Req",
            "admin_last_name": "Admin",
            "admin_email": "req.admin@example.com",
            "admin_phone": "9800000003",
            "admin_password": "ReqAdminPass123!",
        }

        response = self.client.post(request_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])

        hospital = Hospital.objects.get(email=payload["hospital_email"])
        self.assertEqual(hospital.status, Hospital.Status.PENDING)
        self.assertFalse(hospital.is_verified)

        admin_user = User.objects.get(email=payload["admin_email"])
        self.assertEqual(admin_user.role, "hospital_admin")
        self.assertEqual(admin_user.hospital_id, hospital.id)
        self.assertFalse(admin_user.is_active)

    def test_hospital_registration_request_negative_cases(self):
        request_url = reverse("accounts:register-hospital")
        cases = [
            {
                "name": "required_fields_missing",
                "payload": {
                    "hospital_name": "Incomplete Hospital",
                    "hospital_email": "incomplete@example.com",
                    "city": "Kathmandu",
                    "admin_first_name": "NoPhone",
                    "admin_last_name": "Admin",
                    "admin_email": "missing.field.admin@example.com",
                },
            },
            {
                "name": "duplicate_admin_email",
                "payload": {
                    "hospital_name": "Second Request Hospital",
                    "hospital_email": "second.request@example.com",
                    "hospital_phone": "9800000201",
                    "address": "Koteshwor",
                    "city": "Kathmandu",
                    "admin_first_name": "Dup",
                    "admin_last_name": "Email",
                    "admin_email": self.hospital_admin.email,
                    "admin_phone": "9800000202",
                    "admin_password": "AnotherAdminPass123!",
                },
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                response = self.client.post(request_url, case["payload"], format="json")
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertFalse(response.data["success"])
