"""
Core views for MediKit API - health checks and landing page.
"""

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    API Root - Landing page with links to all endpoints.
    Returns JSON with API info and available endpoints.
    """
    return Response({
        'name': 'MediKit API',
        'version': '1.0.0',
        'status': 'ok',
        'description': 'Healthcare platform API for Nepal',
        'endpoints': {
            'docs': '/api/v1/docs/',
            'schema': '/api/v1/schema/',
            'admin': '/admin/',
            'auth': '/api/v1/auth/',
            'hospitals': '/api/v1/hospitals/',
            'doctors': '/api/v1/doctors/',
            'appointments': '/api/v1/appointments/',
            'patients': '/api/v1/patients/',
        },
        'health': '/health/',
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring.
    Returns simple JSON indicating API is healthy.
    """
    return Response({
        'status': 'ok',
        'service': 'medikit-api',
        'message': 'API is running'
    })
