"""
Views for Patient profiles
"""

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsPatient

from .models import PatientProfile
from .serializers import PatientProfileSerializer, PatientProfileUpdateSerializer


class MyProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update current patient's profile.
    
    GET /api/v1/patients/me/
    PATCH /api/v1/patients/me/
    """
    permission_classes = [IsAuthenticated, IsPatient]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PatientProfileUpdateSerializer
        return PatientProfileSerializer
    
    def get_object(self):
        profile, created = PatientProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': PatientProfileSerializer(instance).data
        })
