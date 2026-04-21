"""
Appointment model for booking system
"""

from django.db import models
from django.conf import settings
import uuid


class Appointment(models.Model):
    """
    Appointment booking between patient and doctor.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No Show'
        RESCHEDULED = 'rescheduled', 'Rescheduled'
    
    class Type(models.TextChoices):
        IN_PERSON = 'in_person', 'In Person'
        VIDEO_CALL = 'video_call', 'Video Call'
        PHONE_CALL = 'phone_call', 'Phone Call'
    
    # Unique reference for tracking
    reference_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        db_index=True
    )
    
    # Patient booking
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    
    # Doctor and hospital
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    
    # Appointment timing
    appointment_date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Type
    appointment_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.IN_PERSON
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )
    
    # Reason for visit
    reason = models.TextField(
        blank=True,
        help_text='Primary reason or symptoms'
    )
    disease = models.ForeignKey(
        'hospitals.Disease',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments'
    )
    
    # Additional notes
    patient_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    
    # Fees
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Cancellation
    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments'
    )
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-appointment_date', '-start_time']
        indexes = [
            models.Index(fields=['patient', 'appointment_date']),
            models.Index(fields=['doctor', 'appointment_date']),
            models.Index(fields=['hospital', 'appointment_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.reference_number} - {self.patient} with {self.doctor} on {self.appointment_date}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_reference_number()
        if not self.consultation_fee and self.doctor:
            self.consultation_fee = self.doctor.consultation_fee
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_reference_number():
        """Generate unique reference number"""
        import random
        import string
        from datetime import datetime
        
        date_part = datetime.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"APT-{date_part}-{random_part}"
    
    @property
    def is_upcoming(self):
        from datetime import date
        return self.appointment_date >= date.today() and self.status in [
            self.Status.PENDING, self.Status.CONFIRMED
        ]
    
    @property
    def is_past(self):
        from datetime import date
        return self.appointment_date < date.today() or self.status in [
            self.Status.COMPLETED, self.Status.CANCELLED, self.Status.NO_SHOW
        ]
