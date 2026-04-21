"""
Medical Records models (MVP)
"""

from django.db import models
from django.conf import settings


class MedicalRecord(models.Model):
    """
    Medical record created after consultation.
    """
    
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='medical_record'
    )
    
    # Diagnosis
    diagnosis = models.TextField(help_text='Primary diagnosis')
    diagnosis_codes = models.JSONField(
        default=list,
        blank=True,
        help_text='ICD codes if applicable'
    )
    
    # Clinical notes
    chief_complaint = models.TextField(blank=True)
    history_of_present_illness = models.TextField(blank=True)
    examination_findings = models.TextField(blank=True)
    
    # Prescription
    prescription = models.TextField(blank=True)
    prescription_items = models.JSONField(
        default=list,
        blank=True,
        help_text='Structured prescription: [{medicine, dosage, frequency, duration}]'
    )
    
    # Additional notes
    doctor_notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_instructions = models.TextField(blank=True)
    
    # Created by
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_records'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medical_records'
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
    
    def __str__(self):
        return f"Record for {self.appointment.reference_number}"
