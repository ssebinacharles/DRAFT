from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Optional but highly recommended: OpenAPI 3 documentation
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import (
    CompanyViewSet,
    InternshipPlacementViewSet,
    SupervisorAssignmentViewSet,
    WeeklyLogViewSet,
    FeedbackViewSet,
    EvaluationCriterionViewSet,
    EvaluationViewSet,
    EvaluationScoreViewSet,
    FinalResultViewSet,
    AuditLogViewSet,
    ReportDefinitionViewSet,
    GeneratedReportViewSet,
)

app_name = "issues"

# ============================================================
# ROUTER CONFIGURATION
# ============================================================
# DefaultRouter automatically generates trailing slashes and `.json` format suffixes
router = DefaultRouter()

# 1. Core Entities
router.register(r"companies", CompanyViewSet, basename="company")

# 2. Placements & Assignments
router.register(r"placements", InternshipPlacementViewSet, basename="placement")
router.register(r"supervisor-assignments", SupervisorAssignmentViewSet, basename="supervisor-assignment")

# 3. Supervision & Logs
router.register(r"weekly-logs", WeeklyLogViewSet, basename="weekly-log")
router.register(r"feedback", FeedbackViewSet, basename="feedback")

# 4. Evaluations & Results
router.register(r"evaluation-criteria", EvaluationCriterionViewSet, basename="evaluation-criterion")
router.register(r"evaluations", EvaluationViewSet, basename="evaluation")
router.register(r"evaluation-scores", EvaluationScoreViewSet, basename="evaluation-score")
router.register(r"final-results", FinalResultViewSet, basename="final-result")

# 5. System, Audit & Reporting
router.register(r"audit-logs", AuditLogViewSet, basename="audit-log")
router.register(r"report-definitions", ReportDefinitionViewSet, basename="report-definition")
router.register(r"generated-reports", GeneratedReportViewSet, basename="generated-report")

# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [
    # The core API endpoints (Version 1)
    path("v1/", include(router.urls)),

    # --------------------------------------------------------
    # API DOCUMENTATION (Swagger & ReDoc)
    # --------------------------------------------------------
    # Generates the raw OpenAPI YAML/JSON schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    
    # Swagger UI: Great for testing API calls directly in the browser
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="issues:schema"),
        name="swagger-ui",
    ),
    
    # ReDoc: Great for clean, reading-focused documentation
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="issues:schema"),
        name="redoc",
    ),
]