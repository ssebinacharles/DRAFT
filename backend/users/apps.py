import logging
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register, Tags
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

class UsersConfig(AppConfig):
    """
    Advanced configuration for the ILES1 Identity & Access Management (Users) app.
    Handles initialization, robust signal registration, and pre-flight security checks.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = _("Identity & Access Management")

    def ready(self) -> None:
        """
        Executes once when the Django application registry is fully populated.
        """
        # 1. Safely import signals to avoid circular import crashes during migrations
        try:
            from . import signals  # noqa: F401
            logger.info("Successfully registered Users app signals.")
        except ImportError as e:
            logger.warning(f"Users signals module could not be loaded or is missing: {e}")

        # 2. Register enterprise-level system checks
        self._register_system_checks()

    def _register_system_checks(self) -> None:
        """
        Validates critical security and auth settings before the server boots.
        """
        @register(Tags.security)
        def check_custom_user_model(app_configs: Any, **kwargs: Any) -> list[Error]:
            errors = []

            # Enterprise Check: Ensure the system is actually using THIS custom user model.
            # If a developer forgets this in settings.py, the whole auth system fails.
            expected_model = "users.User"
            if getattr(settings, "AUTH_USER_MODEL", None) != expected_model:
                errors.append(
                    Error(
                        f"AUTH_USER_MODEL is incorrectly configured.",
                        hint=f"Update settings.py to AUTH_USER_MODEL = '{expected_model}'.",
                        obj=self,
                        id="users.E001",
                    )
                )

            return errors
