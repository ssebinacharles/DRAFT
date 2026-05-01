from typing import Any
from django.db.models import Model
from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import UserRole
from .models import SupervisorAssignment

# ============================================================
# OPTIMIZED ROLE & PROFILE HELPERS
# ============================================================

def is_role(user: Any, role: str) -> bool:
    """Safely checks user role without causing attribute errors."""
    return bool(user and user.is_authenticated and getattr(user, 'role', None) == role)

def is_administrator(user: Any) -> bool:
    return is_role(user, UserRole.ADMINISTRATOR)

def is_student(user: Any) -> bool:
    return is_role(user, UserRole.STUDENT)

def is_supervisor(user: Any) -> bool:
    return is_role(user, UserRole.SUPERVISOR)

def get_profile(user: Any, profile_attr: str) -> Model | None:
    """
    Attempts to fetch the profile from the cached reverse relation first
    to prevent N+1 database queries during list views.
    """
    if not user or not user.is_authenticated:
        return None
    # Uses Django's related object cache (e.g., user.studentprofile)
    return getattr(user, profile_attr, None)

# ============================================================
# CORE ACCESS LOGIC
# ============================================================

def can_access_placement(user: Any, placement: Model, read_only: bool = False) -> bool:
    """
    Master gatekeeper for placement access.
    """
    if not user or not user.is_authenticated:
        return False

    if is_administrator(user):
        return True

    if is_student(user):
        profile = get_profile(user, 'studentprofile')
        return bool(profile and placement.student_id == profile.id)

    if is_supervisor(user):
        profile = get_profile(user, 'supervisorprofile')
        if not profile:
            return False
            
        # Optimization: Use exists() for the fastest possible DB check
        return SupervisorAssignment.objects.filter(
            placement=placement,
            supervisor=profile,
            is_active=True
        ).exists()

    return False

# ============================================================
# BASE PERMISSION CLASSES (DRY ARCHITECTURE)
# ============================================================

class BasePlacementPermission(BasePermission):
    """
    Abstract base permission. Children just need to define how to 
    extract the 'placement' object from their specific model.
    """
    def has_permission(self, request: Any, view: Any) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def get_placement(self, obj: Any) -> Model:
        raise NotImplementedError("Subclasses must implement get_placement()")

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        placement = self.get_placement(obj)
        is_safe = request.method in SAFE_METHODS
        
        # Security Hardening: Students should NEVER be able to edit core 
        # evaluation or feedback objects, even if they own the placement.
        if is_student(request.user) and not is_safe:
            # Allow students to submit Weekly Logs, but block other edits
            if not hasattr(obj, 'week_number'): 
                return False

        return can_access_placement(request.user, placement, read_only=is_safe)

# ============================================================
# IMPLEMENTATION CLASSES
# ============================================================

class PlacementPermission(BasePlacementPermission):
    def get_placement(self, obj: Any) -> Model:
        return obj  # The object itself is the placement

class WeeklyLogPermission(BasePlacementPermission):
    def get_placement(self, obj: Any) -> Model:
        return obj.placement

class FeedbackPermission(BasePlacementPermission):
    def get_placement(self, obj: Any) -> Model:
        return obj.weekly_log.placement

class EvaluationPermission(BasePlacementPermission):
    def get_placement(self, obj: Any) -> Model:
        return obj.placement

class EvaluationScorePermission(BasePlacementPermission):
    def get_placement(self, obj: Any) -> Model:
        return obj.evaluation.placement

class FinalResultPermission(BasePlacementPermission):
    def get_placement(self, obj: Any) -> Model:
        return obj.placement

# ============================================================
# SPECIALIZED PERMISSIONS
# ============================================================

class CompanyPermission(BasePermission):
    """Anyone authenticated can read. Only Admins can modify."""
    def has_permission(self, request: Any, view: Any) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_administrator(request.user)

class SupervisorAssignmentPermission(BasePermission):
    def has_permission(self, request: Any, view: Any) -> bool:
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        if is_administrator(request.user):
            return True
            
        # Non-admins can only READ assignments, never create/update/delete
        if request.method not in SAFE_METHODS:
            return False

        if is_student(request.user):
            profile = get_profile(request.user, 'studentprofile')
            return bool(profile and obj.placement.student_id == profile.id)

        if is_supervisor(request.user):
            profile = get_profile(request.user, 'supervisorprofile')
            return bool(profile and obj.supervisor_id == profile.id)

        return False

class EvaluationCriterionPermission(BasePermission):
    def has_permission(self, request: Any, view: Any) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_administrator(request.user)

class IsAdminOnlyPermission(BasePermission):
    """Reusable permission for AuditLogs and Reports."""
    def has_permission(self, request: Any, view: Any) -> bool:
        return is_administrator(request.user)

    def has_object_permission(self, request: Any, view: Any, obj: Any) -> bool:
        return is_administrator(request.user)