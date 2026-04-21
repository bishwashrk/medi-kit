from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.serializers import (
    DoctorRegistrationSerializer,
    HospitalAdminRegistrationSerializer,
)
from apps.doctors.models import AvailabilitySlot, DoctorProfile
from apps.hospitals.models import Department, Hospital


User = get_user_model()


class RoleSerializerValidationTestCase(TestCase):
    def setUp(self):
        self.hospital_a = Hospital.objects.create(
            name="Hospital A",
            slug="hospital-a",
            city="Kathmandu",
            status=Hospital.Status.ACTIVE,
            is_verified=True,
        )
        self.hospital_b = Hospital.objects.create(
            name="Hospital B",
            slug="hospital-b",
            city="Lalitpur",
            status=Hospital.Status.ACTIVE,
            is_verified=True,
        )

        self.department_b = Department.objects.create(
            hospital=self.hospital_b,
            name="Radiology",
            slug="radiology",
            is_active=True,
        )

        User.objects.create_user(
            email="existing.hadmin@example.com",
            password="StrongPass123!",
            first_name="Existing",
            last_name="Admin",
            role="hospital_admin",
            hospital=self.hospital_a,
        )

    def test_hospital_admin_serializer_negative_cases(self):
        cases = [
            {
                "name": "duplicate_hospital_admin",
                "data": {
                    "email": "new.hadmin@example.com",
                    "password": "StrongPass123!",
                    "first_name": "New",
                    "last_name": "Admin",
                    "phone": "9800000010",
                    "hospital_id": self.hospital_a.id,
                },
            },
            {
                "name": "unknown_hospital",
                "data": {
                    "email": "new.hadmin2@example.com",
                    "password": "StrongPass123!",
                    "first_name": "New",
                    "last_name": "Admin",
                    "phone": "9800000011",
                    "hospital_id": 999999,
                },
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                serializer = HospitalAdminRegistrationSerializer(data=case["data"])
                self.assertFalse(serializer.is_valid())
                self.assertIn("hospital_id", serializer.errors)

    def test_doctor_serializer_negative_cases(self):
        cases = [
            {
                "name": "missing_department_and_specialization",
                "data": {
                    "email": "new.doctor@example.com",
                    "password": "StrongPass123!",
                    "first_name": "Doc",
                    "last_name": "NoDept",
                    "phone": "9800000020",
                },
            },
            {
                "name": "department_from_other_hospital",
                "data": {
                    "email": "cross.hospital.doctor@example.com",
                    "password": "StrongPass123!",
                    "first_name": "Cross",
                    "last_name": "Hospital",
                    "phone": "9800000021",
                    "department_id": self.department_b.id,
                },
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                serializer = DoctorRegistrationSerializer(
                    data=case["data"],
                    context={"hospital": self.hospital_a},
                )
                self.assertFalse(serializer.is_valid())
                self.assertIn("department_id", serializer.errors)

    def test_doctor_serializer_creates_doctor_profile_and_default_slots(self):
        serializer = DoctorRegistrationSerializer(
            data={
                "email": "created.doctor@example.com",
                "password": "StrongPass123!",
                "first_name": "Created",
                "last_name": "Doctor",
                "phone": "9800000022",
                "department_name": "Cardiology",
                "experience_years": 5,
                "consultation_fee": "1200.00",
            },
            context={"hospital": self.hospital_a},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()

        created_user = result["user"]
        created_profile = result["doctor_profile"]

        self.assertEqual(created_user.role, "doctor")
        self.assertEqual(created_user.hospital_id, self.hospital_a.id)
        self.assertEqual(created_profile.hospital_id, self.hospital_a.id)
        self.assertTrue(DoctorProfile.objects.filter(user=created_user).exists())
        self.assertEqual(AvailabilitySlot.objects.filter(doctor=created_profile).count(), 6)
