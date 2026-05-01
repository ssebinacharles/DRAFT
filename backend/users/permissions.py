from rest_framework import permissions

# ============================================================
# ROLE HELPER FUNCTIONS
# ============================================================

def is_student(user):
    """Returns True if the user is a Student."""
    return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'STUDENT')

def is_supervisor(user):
    """Returns True if the user is a Supervisor (Academic or Workplace)."""
    return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'SUPERVISOR')

def is_administrator(user):
    """Returns True if the user is an Administrator."""
    return bool(user and user.is_authenticated and getattr(user, 'role', '') == 'ADMINISTRATOR')


# ============================================================
# PROFILE RETRIEVAL HELPERS
# ============================================================

def get_student_profile(user):
    """Safely retrieves the student profile for a user."""
    if hasattr(user, 'studentprofile'):
        return user.studentprofile
    return None

def get_supervisor_profile(user):
    """Safely retrieves the supervisor profile for a user."""
    if hasattr(user, 'supervisorprofile'):
        return user.supervisorprofile
    return None

def get_admin_profile(user):
    """Safely retrieves the administrator profile for a user."""
    if hasattr(user, 'administratorprofile'):
        return user.administratorprofile
    return None


# ============================================================
# DRF PERMISSION CLASSES
# ============================================================

class UserPermission(permissions.BasePermission):
    """Basic permission requiring authentication to view/edit users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class StudentProfilePermission(permissions.BasePermission):
    """Students can access their own, Admins can access all."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class SupervisorProfilePermission(permissions.BasePermission):
    """Supervisors can access their own, Admins can access all."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class AdministratorProfilePermission(permissions.BasePermission):
    """Strictly limits this endpoint to Administrators."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_administrator(request.user)

class IsAdminOnlyPermission(permissions.BasePermission):
    """Reusable permission for any view/action that requires an Admin."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_administrator(request.user)