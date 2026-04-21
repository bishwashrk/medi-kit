from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'diagnosis', 'created_by', 'created_at']
    search_fields = ['appointment__reference_number', 'diagnosis']
