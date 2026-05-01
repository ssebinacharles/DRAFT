import logging
from typing import Any

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register, Tags
from django.utils.translation import gettext_lazy as _

# Initialize a dedicated logger for this app
logger = logging.getLogger(__name__)

class IssuesConfig(AppConfig):
    """
    Advanced configuration for the ILES1 Issues application.
    Handles app initialization, signal mapping, and pre-flight system checks.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "issues"
    
    # Use translation hooks for a more professional admin interface
    verbose_name = _("Issue Tracking & Management")

    def ready(self) -> None:
        """
        Executes once when the Django application registry is fully populated.
        """
        # 1. Safely import signals to prevent application crashes during migrations
        try:
            from . import signals  # noqa: F401
            logger.info("Successfully registered Issues app signals.")
        except ImportError as e:
            logger.warning(f"Issues signals module could not be loaded or is missing: {e}")

        # 2. Initialize critical system configuration checks
        self._register_system_checks()

    def _register_system_checks(self) -> None:
        """
        Registers Django System Checks specific to the Issues app.
        These run during `manage.py runserver` or `manage.py check` to ensure
        the app is perfectly configured before it accepts live traffic.
        """
        @register(Tags.compatibility)
        def check_issues_settings(app_configs: Any, **kwargs: Any) -> list[Error]:
            errors = []
            
            # Example Enterprise Check: 
            # Ensure the system has a support email defined in settings.py 
            # so the issues app knows where to route critical alerts.
            if getattr(settings, "DEBUG", False) is False:
                if not hasattr(settings, "DEFAULT_FROM_EMAIL"):
                    errors.append(
                        Error(
                            "Missing DEFAULT_FROM_EMAIL in settings.",
                            hint="The Issues app requires an email configuration to send notifications in production.",
                            obj=self,
                            id="issues.E001",
                        )
                    )
                    
            return errors