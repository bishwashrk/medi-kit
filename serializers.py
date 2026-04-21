"""
Serializers for Patient profiles
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PatientProfile

User = get_user_model()


class PatientUserSerializer(serializers.ModelSerializer):
    """Nested user info for patient"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'phone', 'avatar']


class PatientProfileSerializer(serializers.ModelSerializer):
    """Patient profile serializer"""
    user = PatientUserSerializer(read_only=True)
    age = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user',
            'date_of_birth', 'age', 'gender', 'blood_group',
            'address', 'city', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'allergies', 'chronic_conditions',
            'created_at', 'updated_at'
        ]


class PatientProfileUpdateSerializer(serializers.ModelSerializer):
    """Update patient profile"""
    
    class Meta:
        model = PatientProfile
        fields = [
            'date_of_birth', 'gender', 'blood_group',
            'address', 'city', 'state', 'postal_code',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'allergies', 'chronic_conditions'
        ]
