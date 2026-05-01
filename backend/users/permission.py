from typing import Any
from django.db.models import Model
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import UserRole

# ============================================================
# OPTIMIZED ROLE & PROFILE HELPERS
# (These should be imported by other apps, like 'issues')
# ============================================================

def is_role(user: Any, role: str) -> bool:
    """Safely checks user role without causing attribute errors on AnonymousUsers."""
    return bool(user and user.is_authenticated and getattr(user, 'role', None) == role)

def is_administrator(user: Any) -> bool:
    return is_role(user, UserRole.ADMINISTRATOR)

def is_student(user: Any) -> bool:
    return is_role(user, UserRole.STUDENT)

def is_supervisor(user: Any) -> bool:
    return is_role(user, UserRole.SUPERVISOR)

def get_profile(user: Any, related_name: str) -> Model | None:
    """
    Attempts to fetch the profile from the cached reverse relation first
    to prevent N+1 database queries during API serialization.
    """
    if not user or not user.is_authenticated:
        return None
    # Relies on the 'related_name' defined in the OneToOneField (e.g., user.student_profile)
    return getattr(user, related_name, None)

def get_student_profile(user: Any) -> Model | None:
    return get_profile(user, "student_profile")

def get_supervisor_profile(user: Any) -> Model | None:
    return get_profile(user, "supervisor_profile")

def get_admin_profile(user: Any) -> Model | None:
    return get_profile(user, "administrator_profile")

# ============================================================
# DRF PERMISSION CLASSES
# ============================================================

class IsAdminOnlyPermission(BasePermission):
    """Reusable permission strictly for Administrators."""
    def has_permission(self, request: Any, view: Any) -> bool:
        return is_administrator(request.user)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        return is_administrator(request.user)


class UserPermission(BasePermission):
    """
    Admins can view/edit all users.
    Standard users can view/edit their OWN user record.
    """
    def has_permission(self, request: Any, view: Any) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        if is_administrator(request.user):
            return True
        return obj == request.user


class StudentProfilePermission(BasePermission):
    """
    Admins have full control.
    Students can READ their own profile. Editing is restricted to admins
    to prevent students from changing their registered course/department.
    """
    def has_permission(self, request: Any, view: Any) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        if is_administrator(request.user):
            return True

        if is_student(request.user) and obj.user == request.user:
            # Force students to read-only mode for their profile data
            return request.method in SAFE_METHODS

        return False


class SupervisorProfilePermission(BasePermission):
    """
    Admins have full control.
    Supervisors can view/edit their own profile details.
    """
    def has_permission(self, request: Any, view: Any) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        if is_administrator(request.user):
            return True

        if is_supervisor(request.user):
            return obj.user == request.user

        return False


class AdministratorProfilePermission(IsAdminOnlyPermission):
    """
    Inherits from the reusable IsAdminOnlyPermission.
    Only Admins should even know this endpoint exists.
    """
    pass