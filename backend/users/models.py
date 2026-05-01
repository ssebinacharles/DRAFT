from __future__ import annotations
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


# ============================================================
# BASE MODELS
# ============================================================

class ILESBaseModel(models.Model):
    """
    Standardized base model with UUIDs and indexed timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserRole(models.TextChoices):
    STUDENT = "STUDENT", _("Student")
    SUPERVISOR = "SUPERVISOR", _("Supervisor")
    ADMINISTRATOR = "ADMINISTRATOR", _("Administrator")


# ============================================================
# CUSTOM USER MANAGER
# ============================================================

class ILESUserManager(BaseUserManager):
    """
    Custom manager required to gracefully handle the custom `role` 
    field during user creation and CLI superuser generation.
    """
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        
        # Default to STUDENT if no role is provided
        extra_fields.setdefault("role", UserRole.STUDENT)
        
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("role", UserRole.ADMINISTRATOR) # Force Admin Role

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(username, email, password, **extra_fields)


# ============================================================
# CORE USER MODEL
# ============================================================

class User(AbstractUser):
    # Using UUIDs for the User model hardens the system against ID scraping
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    phone_number = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    objects = ILESUserManager()

    class Meta:
        ordering = ["username"]
        permissions = [
            ("can_manage_roles", "Can manage user roles"),
        ]

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT

    @property
    def is_supervisor(self) -> bool:
        return self.role == UserRole.SUPERVISOR

    @property
    def is_administrator(self) -> bool:
        return self.role == UserRole.ADMINISTRATOR


# ============================================================
# PROFILE MODELS
# ============================================================

class StudentProfile(ILESBaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    registration_number = models.CharField(max_length=50, unique=True, db_index=True)
    course = models.CharField(max_length=150)
    year_of_study = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    department = models.CharField(max_length=150)

    class Meta:
        ordering = ["registration_number"]

    def clean(self) -> None:
        super().clean()
        if hasattr(self, 'user') and self.user.role != UserRole.STUDENT:
            raise ValidationError({"user": _("StudentProfile can only be linked to a STUDENT user.")})

    def save(self, *args, **kwargs):
        self.full_clean()  # Force validation on every save
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.registration_number} - {self.user.get_full_name() or self.user.username}"


class SupervisorType(models.TextChoices):
    ACADEMIC = "ACADEMIC", _("Academic Supervisor")
    WORKPLACE = "WORKPLACE", _("Workplace Supervisor")


class SupervisorProfile(ILESBaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="supervisor_profile")
    supervisor_type = models.CharField(max_length=20, choices=SupervisorType.choices)
    organization_name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["user__username"]

    def clean(self) -> None:
        super().clean()
        if hasattr(self, 'user') and self.user.role != UserRole.SUPERVISOR:
            raise ValidationError({"user": _("SupervisorProfile can only be linked to a SUPERVISOR user.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.user.get_full_name() or self.user.username} - {self.get_supervisor_type_display()}"


class AdministratorProfile(ILESBaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="administrator_profile")
    office_name = models.CharField(max_length=150, default="Internship Office")

    class Meta:
        ordering = ["user__username"]

    def clean(self) -> None:
        super().clean()
        if hasattr(self, 'user') and self.user.role != UserRole.ADMINISTRATOR:
            raise ValidationError({"user": _("AdministratorProfile can only be linked to an ADMINISTRATOR user.")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.user.get_full_name() or self.user.username