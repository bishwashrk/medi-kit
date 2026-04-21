"""
URL routes for patients
"""

from django.urls import path
from .views import MyProfileView

app_name = 'patients'

urlpatterns = [
    path('me/', MyProfileView.as_view(), name='my-profile'),
]
