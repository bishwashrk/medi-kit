"""
Chat models for patient-doctor messaging (MVP)
"""

from django.db import models
from django.conf import settings


class ChatThread(models.Model):
    """
    Chat thread linked to an appointment.
    """
    
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='chat_thread'
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_chat_threads'
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_chat_threads'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_threads'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat: {self.patient} - {self.doctor}"


class Message(models.Model):
    """
    Individual message in a chat thread.
    """
    
    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    
    content = models.TextField()
    
    # Attachment (optional)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender} at {self.created_at}"
