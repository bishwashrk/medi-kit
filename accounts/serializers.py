"""
Serializers for authentication and user management
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from datetime import time

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details (read-only sensitive fields)"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'hospital', 'hospital_name', 'avatar',
            'is_active', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for patient registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # Patients register themselves
        validated_data['role'] = 'patient'
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extended JWT token serializer with user info"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        if user.hospital:
            token['hospital_id'] = user.hospital.id
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.user.get_full_name(),
            'role': self.user.role,
            'hospital_id': self.user.hospital_id,
            'avatar': self.user.avatar.url if self.user.avatar else None,
        }
        
        return data


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar']


# ============= SUPER ADMIN SERIALIZERS =============

class HospitalAdminRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a Hospital Admin account.
    Only Super Admins can use this.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    hospital_id = serializers.IntegerField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'first_name', 'last_name', 
            'phone', 'hospital_id'
        ]
    
    def validate_hospital_id(self, value):
        from apps.hospitals.models import Hospital
        try:
            hospital = Hospital.objects.get(id=value)
            # Check if hospital already has an admin
            if User.objects.filter(hospital_id=value, role='hospital_admin').exists():
                raise serializers.ValidationError(
                    'This hospital already has an admin account.'
                )
            return value
        except Hospital.DoesNotExist:
            raise serializers.ValidationError('Hospital not found.')
    
    def create(self, validated_data):
        hospital_id = validated_data.pop('hospital_id')
        from apps.hospitals.models import Hospital
        hospital = Hospital.objects.get(id=hospital_id)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            role='hospital_admin',
            hospital=hospital,
            is_verified=True,  # Admin-created accounts are pre-verified
        )
        return user


class HospitalRegistrationSerializer(serializers.Serializer):
    """
    Serializer for registering a new hospital with its admin account.
    Only Super Admins can use this.
    """
    
    # Hospital fields
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    website = serializers.URLField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100, required=False, allow_blank=True)
    postal_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    latitude = serializers.DecimalField(max_digits=10, decimal_places=8, required=False, allow_null=True)
    longitude = serializers.DecimalField(max_digits=11, decimal_places=8, required=False, allow_null=True)
    is_emergency_available = serializers.BooleanField(default=False)
    is_ambulance_available = serializers.BooleanField(default=False)
    
    # Hospital Admin fields
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True, min_length=8)
    admin_first_name = serializers.CharField(max_length=150)
    admin_last_name = serializers.CharField(max_length=150)
    admin_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    def validate_admin_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
    def create(self, validated_data):
        from apps.hospitals.models import Hospital
        
        # Extract admin fields
        admin_email = validated_data.pop('admin_email')
        admin_password = validated_data.pop('admin_password')
        admin_first_name = validated_data.pop('admin_first_name')
        admin_last_name = validated_data.pop('admin_last_name')
        admin_phone = validated_data.pop('admin_phone', '')
        
        # Create hospital
        hospital = Hospital.objects.create(
            name=validated_data.get('name'),
            description=validated_data.get('description', ''),
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            website=validated_data.get('website', ''),
            address=validated_data.get('address', ''),
            city=validated_data.get('city', ''),
            state=validated_data.get('state', ''),
            postal_code=validated_data.get('postal_code', ''),
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            is_emergency_available=validated_data.get('is_emergency_available', False),
            is_ambulance_available=validated_data.get('is_ambulance_available', False),
            status='active',
            is_verified=True,
        )
        
        # Create hospital admin
        admin_user = User.objects.create_user(
            email=admin_email,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name,
            phone=admin_phone,
            role='hospital_admin',
            hospital=hospital,
            is_verified=True,
        )
        
        return {
            'hospital': hospital,
            'admin': admin_user,
            'admin_password': admin_password,  # Return password for display (one time)
        }


class HospitalAdminListSerializer(serializers.ModelSerializer):
    """Serializer for listing hospital admins"""
    
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'hospital', 'hospital_name', 'is_active', 
            'is_verified', 'date_joined'
        ]


# ============= HOSPITAL ADMIN SERIALIZERS =============

class DoctorRegistrationSerializer(serializers.Serializer):
    """
    Serializer for registering a new doctor.
    Hospital Admins can use this for their hospital.
    """
    
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    
    # Doctor profile fields
    department_id = serializers.IntegerField(required=False, allow_null=True)
    specialization_id = serializers.IntegerField(required=False, allow_null=True)
    specialization = serializers.CharField(max_length=255, required=False, allow_blank=True)
    department_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    license_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    qualification = serializers.CharField(max_length=255, required=False, allow_blank=True)
    experience_years = serializers.IntegerField(default=0)
    bio = serializers.CharField(required=False, allow_blank=True)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
    def validate_department_id(self, value):
        if value:
            from apps.hospitals.models import Department
            hospital = self.context.get('hospital')
            if hospital and not Department.objects.filter(id=value, hospital=hospital).exists():
                raise serializers.ValidationError('Department not found in your hospital.')
        return value

    def validate(self, attrs):
        department_id = attrs.get('department_id')
        specialization_id = attrs.get('specialization_id')
        department_name = (attrs.get('department_name') or '').strip()
        specialization_name = (attrs.get('specialization') or '').strip()

        if not any([department_id, specialization_id, department_name, specialization_name]):
            raise serializers.ValidationError({
                'department_id': 'Select a department or specialization when registering doctor.'
            })

        # Keep behavior consistent for clients that only send specialization text.
        if not department_name and specialization_name:
            attrs['department_name'] = specialization_name

        return attrs
    
    def create(self, validated_data):
        from apps.doctors.models import DoctorProfile, AvailabilitySlot
        from apps.hospitals.models import Department, Specialization
        
        hospital = self.context.get('hospital')
        
        # Extract doctor profile fields
        department_id = validated_data.pop('department_id', None)
        specialization_id = validated_data.pop('specialization_id', None)
        specialization_name = (validated_data.pop('specialization', '') or '').strip()
        department_name = (validated_data.pop('department_name', '') or '').strip()
        license_number = validated_data.pop('license_number', '')
        qualification = validated_data.pop('qualification', '')
        experience_years = validated_data.pop('experience_years', 0)
        bio = validated_data.pop('bio', '')
        consultation_fee = validated_data.pop('consultation_fee', 0)

        if not hospital:
            raise serializers.ValidationError({'hospital': 'Hospital context is required.'})
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            role='doctor',
            hospital=hospital,
            is_verified=True,
        )
        
        # Get related objects
        department = None
        if department_id:
            department = Department.objects.filter(id=department_id, hospital=hospital).first()
        elif department_name or specialization_name:
            auto_department_name = department_name or specialization_name
            department = Department.objects.filter(
                hospital=hospital,
                name__iexact=auto_department_name,
            ).first()
            if not department:
                department_slug = slugify(auto_department_name)
                if not department_slug:
                    department_slug = f'department-{hospital.id}'
                base_slug = department_slug
                counter = 1
                while Department.objects.filter(hospital=hospital, slug=department_slug).exists():
                    department_slug = f'{base_slug}-{counter}'
                    counter += 1
                department = Department.objects.create(
                    hospital=hospital,
                    name=auto_department_name,
                    slug=department_slug,
                    is_active=True,
                )
        else:
            # Final safety net for inconsistent clients: place doctor in General Medicine.
            auto_department_name = 'General Medicine'
            department = Department.objects.filter(
                hospital=hospital,
                name__iexact=auto_department_name,
            ).first()
            if not department:
                department_slug = slugify(auto_department_name)
                base_slug = department_slug
                counter = 1
                while Department.objects.filter(hospital=hospital, slug=department_slug).exists():
                    department_slug = f'{base_slug}-{counter}'
                    counter += 1
                department = Department.objects.create(
                    hospital=hospital,
                    name=auto_department_name,
                    slug=department_slug,
                    is_active=True,
                )
        
        specialization = None
        if specialization_id:
            specialization = Specialization.objects.filter(id=specialization_id).first()
        elif specialization_name:
            specialization = Specialization.objects.filter(name__iexact=specialization_name).first()
            if not specialization:
                specialization_slug = slugify(specialization_name)
                if not specialization_slug:
                    specialization_slug = 'general-medicine'
                base_slug = specialization_slug
                counter = 1
                while Specialization.objects.filter(slug=specialization_slug).exists():
                    specialization_slug = f'{base_slug}-{counter}'
                    counter += 1
                specialization = Specialization.objects.create(
                    name=specialization_name,
                    slug=specialization_slug,
                    is_active=True,
                )
        elif department and department.name:
            specialization = Specialization.objects.filter(name__iexact=department.name).first()
            if not specialization:
                specialization_slug = slugify(department.name) or 'general-medicine'
                base_slug = specialization_slug
                counter = 1
                while Specialization.objects.filter(slug=specialization_slug).exists():
                    specialization_slug = f'{base_slug}-{counter}'
                    counter += 1
                specialization = Specialization.objects.create(
                    name=department.name,
                    slug=specialization_slug,
                    is_active=True,
                )
        
        # Create doctor profile
        doctor_profile = DoctorProfile.objects.create(
            user=user,
            hospital=hospital,
            department=department,
            specialization=specialization,
            license_number=license_number,
            qualification=qualification,
            experience_years=experience_years,
            bio=bio,
            consultation_fee=consultation_fee,
        )

        # Ensure new doctors have a baseline weekly schedule so booking doesn't show empty slots.
        # 0=Sunday ... 6=Saturday. Nepal default working days are commonly Sunday-Friday.
        if not AvailabilitySlot.objects.filter(doctor=doctor_profile).exists():
            default_slots = [
                AvailabilitySlot(
                    doctor=doctor_profile,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(17, 0),
                    max_appointments=doctor_profile.max_patients_per_slot,
                    is_active=True,
                )
                for day in [0, 1, 2, 3, 4, 5]
            ]
            AvailabilitySlot.objects.bulk_create(default_slots)
        
        return {
            'user': user,
            'doctor_profile': doctor_profile,
        }
