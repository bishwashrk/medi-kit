"""
Serializers for Appointments
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import datetime, date

from apps.doctors.serializers import DoctorListSerializer
from apps.hospitals.serializers import HospitalListSerializer

from .models import Appointment

User = get_user_model()


class PatientMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone']


class AppointmentListSerializer(serializers.ModelSerializer):
    """Lightweight appointment serializer for listings"""
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    doctor_avatar = serializers.ImageField(source='doctor.user.avatar', read_only=True)
    hospital_logo = serializers.ImageField(source='hospital.logo', read_only=True)
    hospital_cover_image = serializers.ImageField(source='hospital.cover_image', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'reference_number',
            'patient', 'patient_name',
            'doctor', 'doctor_name',
            'doctor_avatar',
            'hospital', 'hospital_name',
            'hospital_logo', 'hospital_cover_image',
            'appointment_date', 'start_time', 'end_time',
            'appointment_type', 'type_display',
            'status', 'status_display',
            'disease', 'disease_name',
            'consultation_fee',
            'created_at'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Full appointment details"""
    patient = PatientMinimalSerializer(read_only=True)
    doctor = DoctorListSerializer(read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    doctor_avatar = serializers.ImageField(source='doctor.user.avatar', read_only=True)
    hospital_logo = serializers.ImageField(source='hospital.logo', read_only=True)
    hospital_cover_image = serializers.ImageField(source='hospital.cover_image', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'reference_number',
            'patient', 'doctor',
            'doctor_avatar',
            'hospital', 'hospital_name',
            'hospital_logo', 'hospital_cover_image',
            'appointment_date', 'start_time', 'end_time',
            'appointment_type', 'status', 'status_display',
            'reason', 'disease', 'disease_name',
            'patient_notes', 'doctor_notes',
            'consultation_fee',
            'cancelled_by', 'cancellation_reason', 'cancelled_at',
            'created_at', 'updated_at'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Create new appointment (by patient)"""
    
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'hospital',
            'appointment_date', 'start_time', 'end_time',
            'appointment_type',
            'reason', 'disease',
            'patient_notes'
        ]
    
    def validate_appointment_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Cannot book appointment in the past.")
        return value
    
    def validate(self, attrs):
        doctor = attrs.get('doctor')
        hospital = attrs.get('hospital')
        appointment_date = attrs.get('appointment_date')
        start_time = attrs.get('start_time')
        
        # Validate doctor belongs to hospital
        if doctor.hospital_id != hospital.id:
            raise serializers.ValidationError({
                'doctor': 'Doctor does not belong to the selected hospital.'
            })
        
        # Check if doctor is accepting appointments
        if not doctor.is_accepting_appointments:
            raise serializers.ValidationError({
                'doctor': 'Doctor is not currently accepting appointments.'
            })
        
        # Check for conflicting appointments
        existing = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            start_time=start_time,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        ).count()
        
        if existing >= doctor.max_patients_per_slot:
            raise serializers.ValidationError({
                'start_time': 'This time slot is fully booked.'
            })
        
        return attrs
    
    def create(self, validated_data):
        # Set patient from request
        validated_data['patient'] = self.context['request'].user
        
        # Set consultation fee from doctor
        if 'consultation_fee' not in validated_data:
            validated_data['consultation_fee'] = validated_data['doctor'].consultation_fee
        
        return super().create(validated_data)


class AppointmentCancelSerializer(serializers.Serializer):
    """Cancel appointment"""
    reason = serializers.CharField(required=False, allow_blank=True)


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    """Update appointment status (by doctor/hospital admin)"""
    status = serializers.ChoiceField(choices=Appointment.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
