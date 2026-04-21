"""
URL configuration for MediKit project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core.views import api_root, health_check

urlpatterns = [
    # Root endpoint - API landing page
    path('', api_root, name='api-root'),
    
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include([
        path('auth/', include('apps.accounts.urls')),
        path('hospitals/', include('apps.hospitals.urls')),
        path('doctors/', include('apps.doctors.urls')),
        path('patients/', include('apps.patients.urls')),
        path('appointments/', include('apps.appointments.urls')),
        path('records/', include('apps.records.urls')),
        path('payments/', include('apps.payments.urls')),
        path('chat/', include('apps.chat.urls')),
    ])),
    
    # API Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
