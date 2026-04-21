#!/usr/bin/env python
"""Create test accounts for testing admin workflows"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medikit.settings')
django.setup()

from apps.accounts.models import User
from apps.hospitals.models import Hospital

print("\n🔧 Creating Test Accounts for MediKit\n" + "="*40)

# Create Super Admin
super_admin, created = User.objects.get_or_create(
    email='superadmin@medikit.com',
    defaults={
        'first_name': 'Super',
        'last_name': 'Admin',
        'role': 'super_admin',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    super_admin.set_password('admin123')
    super_admin.save()
    print('✅ Super Admin CREATED')
else:
    print('ℹ️  Super Admin already exists')

print(f'   📧 Email: superadmin@medikit.com')
print(f'   🔑 Password: admin123')
print(f'   🔗 Dashboard: http://localhost:3000/super-admin')
print()

# Create a pending hospital for testing
pending_hospital, created = Hospital.objects.get_or_create(
    slug='pending-test-hospital',
    defaults={
        'name': 'Pending Test Hospital',
        'city': 'Kathmandu',
        'address': 'Test Address, Kathmandu',
        'status': 'pending',
        'is_verified': False,
        'latitude': 27.7172,
        'longitude': 85.3240,
    }
)
if created:
    print('✅ Pending Hospital CREATED (for approval testing)')
    print(f'   🏥 Name: {pending_hospital.name}')
    print()

# Get an active hospital for hospital admin
hospital = Hospital.objects.filter(status='active').first()
if not hospital:
    hospital = Hospital.objects.first()
    if hospital:
        hospital.status = 'active'
        hospital.is_verified = True
        hospital.save()
        print(f'✅ Activated hospital: {hospital.name}')

if hospital:
    # Create Hospital Admin
    hospital_admin, created = User.objects.get_or_create(
        email='hospitaladmin@medikit.com',
        defaults={
            'first_name': 'Hospital',
            'last_name': 'Admin',
            'role': 'hospital_admin',
            'hospital': hospital,
        }
    )
    if created:
        hospital_admin.set_password('admin123')
        hospital_admin.save()
        print('✅ Hospital Admin CREATED')
    else:
        # Ensure hospital is linked
        if not hospital_admin.hospital:
            hospital_admin.hospital = hospital
            hospital_admin.save()
        print('ℹ️  Hospital Admin already exists')
    
    print(f'   📧 Email: hospitaladmin@medikit.com')
    print(f'   🔑 Password: admin123')
    print(f'   🏥 Hospital: {hospital_admin.hospital.name if hospital_admin.hospital else "None"}')
    print(f'   🔗 Dashboard: http://localhost:3000/hospital-admin')
else:
    print('⚠️  No hospital found to link Hospital Admin to')

print()
print("="*40)

# Stats
pending_count = Hospital.objects.filter(status='pending').count()
active_count = Hospital.objects.filter(status='active').count()
total_doctors = User.objects.filter(role='doctor').count()

print(f"📊 Current Stats:")
print(f"   🏥 Pending Hospitals: {pending_count}")
print(f"   ✅ Active Hospitals: {active_count}")
print(f"   👨‍⚕️ Total Doctors: {total_doctors}")
print()
print("🎯 Ready to test! Open http://localhost:3000/login")
