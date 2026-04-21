"""
Custom User Model with Role-Based Access Control (RBAC)
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """User role choices for RBAC"""
    SUPER_ADMIN = 'super_admin', 'Super Admin'
    HOSPITAL_ADMIN = 'hospital_admin', 'Hospital Admin'
    DOCTOR = 'doctor', 'Doctor'
    PATIENT = 'patient', 'Patient'


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.SUPER_ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier.
    Supports multiple roles with hospital scoping for hospital_admin and doctor.
    """
    
    email = models.EmailField(
        unique=True,
        db_index=True,
        help_text='Unique email address used for authentication'
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Role-based access control
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        db_index=True
    )
    
    # Hospital scoping (for hospital_admin and doctor roles)
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        help_text='Associated hospital (required for hospital_admin and doctor roles)'
    )
    
    # Profile image
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    # Status flags
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(
        default=False,
        help_text='Email verification status'
    )
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['hospital']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return self.first_name or self.email.split('@')[0]
    
    # Role check helpers
    @property
    def is_super_admin(self):
        return self.role == UserRole.SUPER_ADMIN
    
    @property
    def is_hospital_admin(self):
        return self.role == UserRole.HOSPITAL_ADMIN
    
    @property
    def is_doctor(self):
        return self.role == UserRole.DOCTOR
    
    @property
    def is_patient(self):
        return self.role == UserRole.PATIENT
    
    def has_hospital_access(self, hospital_id):
        """Check if user has access to a specific hospital"""
        if self.is_super_admin:
            return True
        if self.hospital_id and self.hospital_id == hospital_id:
            return True
        return False
