import logging
import uuid
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    AdministratorProfile,
    StudentProfile,
    SupervisorProfile,
    SupervisorType,
    UserRole,
)

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_related_user_profile(
    sender: type[User], instance: User, created: bool, **kwargs: Any
) -> None:
    """
    Automatically provisions the correct profile shell when a new User is created.
    Injects placeholder data for strictly required database fields.
    """
    if not created:
        # If the user is just being updated, do nothing.
        return

    try:
        # ============================================================
        # STUDENT PROFILE PROVISIONING
        # ============================================================
        if instance.role == UserRole.STUDENT:
            # Generate a unique temp ID to satisfy the unique=True constraint
            temp_reg_number = f"TEMP-{uuid.uuid4().hex[:8].upper()}"
            
            StudentProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "registration_number": temp_reg_number,
                    "course": "PENDING_SETUP",
                    "department": "PENDING_SETUP",
                    "year_of_study": 1,
                },
            )
            logger.info(f"Provisioned temporary StudentProfile for {instance.username}")

        # ============================================================
        # SUPERVISOR PROFILE PROVISIONING
        # ============================================================
        elif instance.role == UserRole.SUPERVISOR:
            SupervisorProfile.objects.get_or_create(
                user=instance,
                defaults={
                    # Defaulting to workplace; Admins/Supervisors can update this later
                    "supervisor_type": SupervisorType.WORKPLACE,
                    "organization_name": "PENDING_SETUP",
                    "title": "PENDING_SETUP",
                },
            )
            logger.info(f"Provisioned default SupervisorProfile for {instance.username}")

        # ============================================================
        # ADMINISTRATOR PROFILE PROVISIONING
        # ============================================================
        elif instance.role == UserRole.ADMINISTRATOR:
            AdministratorProfile.objects.get_or_create(
                user=instance,
                defaults={
                    "office_name": "Internship Office",
                },
            )
            logger.info(f"Provisioned AdministratorProfile for {instance.username}")

    except Exception as e:
        # In an enterprise app, a failed profile creation shouldn't crash the whole 
        # registration flow, but it MUST be logged for the dev team to investigate.
        logger.error(
            f"Failed to provision profile for user {instance.username} (Role: {instance.role}). Error: {str(e)}"
        )


@receiver(post_save, sender=User)
def save_related_user_profile(
    sender: type[User], instance: User, created: bool, **kwargs: Any
) -> None:
    """
    Ensures that if a User is saved, their underlying profile's `updated_at` 
    timestamp is also touched (if needed) or validates profile integrity.
    """
    if created:
        return

    # Using hasattr prevents database queries if the profile doesn't exist
    try:
        if instance.role == UserRole.STUDENT and hasattr(instance, "student_profile"):
            instance.student_profile.save()
            
        elif instance.role == UserRole.SUPERVISOR and hasattr(instance, "supervisor_profile"):
            instance.supervisor_profile.save()
            
        elif instance.role == UserRole.ADMINISTRATOR and hasattr(instance, "administrator_profile"):
            instance.administrator_profile.save()
            
    except Exception as e:
        logger.warning(f"Failed to cascade save profile for {instance.username}: {str(e)}")