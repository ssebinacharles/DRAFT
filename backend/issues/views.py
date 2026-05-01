from __future__ import annotations

from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    AuditLog,
    Company,
    Evaluation,
    EvaluationCriterion,
    EvaluationScore,
    EvaluationStatus,
    Feedback,
    FinalResult,
    GeneratedReport,
    InternshipPlacement,
    PlacementStatus,
    ReportDefinition,
    ReportStatus,
    SupervisorAssignment,
    WeeklyLog,
    WeeklyLogStatus,
)

from .permissions import (
    AuditLogPermission,
    CompanyPermission,
    EvaluationCriterionPermission,
    EvaluationPermission,
    EvaluationScorePermission,
    FeedbackPermission,
    FinalResultPermission,
    IsAdminOnlyPermission,  # Imported the reusable admin permission we made
    PlacementPermission,
    ReportPermission,
    SupervisorAssignmentPermission,
    WeeklyLogPermission,
    can_access_placement,
    get_admin_profile,
    get_student_profile,
    get_supervisor_profile,
    is_administrator,
    is_student,
    is_supervisor,
)

from .serializers import (
    AuditLogSerializer,
    CompanySerializer,
    EvaluationCriterionSerializer,
    EvaluationScoreSerializer,
    EvaluationSerializer,
    FeedbackSerializer,
    FinalResultSerializer,
    GeneratedReportSerializer,
    InternshipPlacementSerializer,
    ReportDefinitionSerializer,
    SupervisorAssignmentSerializer,
    WeeklyLogSerializer,
)

# ============================================================
# ENTERPRISE CORE MIXINS
# ============================================================

class ILESBaseViewSet(viewsets.ModelViewSet):
    """
    Master Base ViewSet. 
    1. Enforces search/ordering defaults.
    2. Automatically triggers Serializer eager loading to prevent N+1 queries.
    3. Automates Role-Based QuerySet filtering (DRY pattern).
    """
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering = ("-id",)
    
    # Subclasses define these to automate queryset filtering
    student_lookup: str | None = None
    supervisor_lookup: str | None = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        # 1. Apply Role-Based Filtering
        if not user or not user.is_authenticated:
            qs = qs.none()
        elif is_administrator(user):
            pass  # Admins see everything
        elif is_student(user) and self.student_lookup:
            profile = get_student_profile(user)
            qs = qs.filter(**{self.student_lookup: profile}) if profile else qs.none()
        elif is_supervisor(user) and self.supervisor_lookup:
            profile = get_supervisor_profile(user)
            qs = qs.filter(**{self.supervisor_lookup: profile, f"{self.supervisor_lookup}_assignments__is_active": True}).distinct() if profile else qs.none()
        else:
            qs = qs.none()

        # 2. Apply Eager Loading from Serializer
        serializer_class = self.get_serializer_class()
        if hasattr(serializer_class, "setup_eager_loading"):
            qs = serializer_class.setup_eager_loading(qs)

        return qs


# ============================================================
# CORE ENTITY VIEWSETS
# ============================================================

class CompanyViewSet(ILESBaseViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [CompanyPermission]
    search_fields = ("company_name", "location", "contact_email", "contact_person_name")
    ordering = ("company_name",)


class InternshipPlacementViewSet(ILESBaseViewSet):
    queryset = InternshipPlacement.objects.all()
    serializer_class = InternshipPlacementSerializer
    permission_classes = [PlacementPermission]
    search_fields = ("student__registration_number", "student__user__username", "company__company_name", "status")
    ordering = ("-requested_at",)

    # Automated Filtering Lookups
    student_lookup = "student"
    supervisor_lookup = "supervisor_assignments__supervisor"

    def perform_create(self, serializer):
        user = self.request.user
        if is_student(user):
            serializer.save(student=get_student_profile(user))
        else:
            serializer.save()

    # Using permission_classes=[IsAdminOnlyPermission] automatically blocks 403s
    @action(detail=True, methods=["post"], permission_classes=[IsAdminOnlyPermission])
    def approve(self, request, pk=None):
        placement = self.get_object()
        placement.status = PlacementStatus.APPROVED
        placement.approved_by = get_admin_profile(request.user)
        placement.approved_at = timezone.now()
        placement.rejection_reason = ""
        placement.save()
        return Response(self.get_serializer(placement).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOnlyPermission])
    def reject(self, request, pk=None):
        placement = self.get_object()
        placement.status = PlacementStatus.REJECTED
        placement.rejection_reason = request.data.get("rejection_reason", "")
        placement.save()
        return Response(self.get_serializer(placement).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOnlyPermission])
    def mark_in_progress(self, request, pk=None):
        placement = self.get_object()
        placement.status = PlacementStatus.IN_PROGRESS
        placement.save()
        return Response(self.get_serializer(placement).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOnlyPermission])
    def complete(self, request, pk=None):
        placement = self.get_object()
        placement.status = PlacementStatus.COMPLETED
        placement.save()
        return Response(self.get_serializer(placement).data)


class SupervisorAssignmentViewSet(ILESBaseViewSet):
    queryset = SupervisorAssignment.objects.all()
    serializer_class = SupervisorAssignmentSerializer
    permission_classes = [SupervisorAssignmentPermission]
    search_fields = ("placement__student__registration_number", "placement__company__company_name", "supervisor__user__username", "assignment_role")
    ordering = ("-assigned_at",)

    student_lookup = "placement__student"
    supervisor_lookup = "supervisor"

    def perform_create(self, serializer):
        serializer.save(assigned_by=get_admin_profile(self.request.user))


# ============================================================
# LOGS & FEEDBACK VIEWSETS
# ============================================================

class WeeklyLogViewSet(ILESBaseViewSet):
    queryset = WeeklyLog.objects.all()
    serializer_class = WeeklyLogSerializer
    permission_classes = [WeeklyLogPermission]
    search_fields = ("title", "status", "placement__student__registration_number", "placement__company__company_name")
    ordering = ("placement", "week_number")

    student_lookup = "placement__student"
    supervisor_lookup = "placement__supervisor_assignments__supervisor"

    def perform_create(self, serializer):
        placement = serializer.validated_data["placement"]
        if is_student(self.request.user) and not can_access_placement(self.request.user, placement):
            # DRF natively catches PermissionError as a 500, we should raise a DRF PermissionDenied for a 403
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only create logs for your own placement.")
        serializer.save()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        log = self.get_object()
        # Ensure only the owner or an admin can submit
        if not (is_administrator(request.user) or (is_student(request.user) and can_access_placement(request.user, log.placement))):
            return Response({"detail": "You cannot submit this log."}, status=status.HTTP_403_FORBIDDEN)

        log.status = WeeklyLogStatus.SUBMITTED
        log.submitted_at = timezone.now()
        log.save()
        return Response(self.get_serializer(log).data)


class FeedbackViewSet(ILESBaseViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [FeedbackPermission]
    search_fields = ("decision", "comment", "supervisor__user__username", "weekly_log__title")
    ordering = ("-created_at",)

    student_lookup = "weekly_log__placement__student"
    supervisor_lookup = "weekly_log__placement__supervisor_assignments__supervisor"

    def perform_create(self, serializer):
        if is_supervisor(self.request.user):
            serializer.save(supervisor=get_supervisor_profile(self.request.user))
        else:
            serializer.save()


# ============================================================
# EVALUATION VIEWSETS
# ============================================================

class EvaluationCriterionViewSet(ILESBaseViewSet):
    queryset = EvaluationCriterion.objects.all()
    serializer_class = EvaluationCriterionSerializer
    permission_classes = [EvaluationCriterionPermission]
    search_fields = ("criterion_name", "criterion_group")
    ordering = ("criterion_group", "criterion_name")


class EvaluationViewSet(ILESBaseViewSet):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer
    permission_classes = [EvaluationPermission]
    search_fields = ("evaluation_type", "status", "placement__student__registration_number", "evaluator__user__username")
    ordering = ("-created_at",)

    student_lookup = "placement__student"
    supervisor_lookup = "placement__supervisor_assignments__supervisor"

    def perform_create(self, serializer):
        if is_supervisor(self.request.user):
            serializer.save(evaluator=get_supervisor_profile(self.request.user))
        else:
            serializer.save()

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        evaluation = self.get_object()
        profile = get_supervisor_profile(request.user)

        if not (is_administrator(request.user) or (is_supervisor(request.user) and profile and evaluation.evaluator_id == profile.id)):
            return Response({"detail": "You cannot submit this evaluation."}, status=status.HTTP_403_FORBIDDEN)

        evaluation.status = EvaluationStatus.SUBMITTED
        evaluation.submitted_at = timezone.now()
        evaluation.save()
        return Response(self.get_serializer(evaluation).data)


class EvaluationScoreViewSet(ILESBaseViewSet):
    queryset = EvaluationScore.objects.all()
    serializer_class = EvaluationScoreSerializer
    permission_classes = [EvaluationScorePermission]
    search_fields = ("criterion__criterion_name", "evaluation__evaluation_type")
    ordering = ("evaluation", "criterion")

    student_lookup = "evaluation__placement__student"
    supervisor_lookup = "evaluation__evaluator"


class FinalResultViewSet(ILESBaseViewSet):
    queryset = FinalResult.objects.all()
    serializer_class = FinalResultSerializer
    permission_classes = [FinalResultPermission]
    search_fields = ("placement__student__registration_number", "placement__company__company_name")
    ordering = ("-published_at",)

    student_lookup = "placement__student"
    supervisor_lookup = "placement__supervisor_assignments__supervisor"

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOnlyPermission])
    def publish(self, request, pk=None):
        final_result = self.get_object()
        final_result.published_by = get_admin_profile(request.user)
        final_result.published_at = timezone.now()
        final_result.save()
        return Response(self.get_serializer(final_result).data)


# ============================================================
# AUDIT & REPORTING VIEWSETS
# ============================================================

class AuditLogViewSet(ILESBaseViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [AuditLogPermission]
    search_fields = ("action", "model_label", "object_id", "actor__username")
    ordering = ("-created_at",)
    
    # Overriding get_queryset since admins are the only ones allowed anyway
    def get_queryset(self):
        qs = super(ILESBaseViewSet, self).get_queryset() # Bypass role filtering
        return qs.select_related("actor", "content_type")


class ReportDefinitionViewSet(ILESBaseViewSet):
    queryset = ReportDefinition.objects.all()
    serializer_class = ReportDefinitionSerializer
    permission_classes = [ReportPermission]
    search_fields = ("name", "report_type", "frequency")
    ordering = ("name",)

    def get_queryset(self):
        qs = super(ILESBaseViewSet, self).get_queryset()
        return qs.select_related("created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminOnlyPermission])
    def run_now(self, request, pk=None):
        report_definition = self.get_object()

        generated_report = GeneratedReport.objects.create(
            report_definition=report_definition,
            generated_by=request.user,
            status=ReportStatus.COMPLETED,
            output_format=request.data.get("output_format", "PDF"),
            summary={"message": "Manual report trigger recorded from API."},
            generated_at=timezone.now(),
        )

        serializer = GeneratedReportSerializer(generated_report, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GeneratedReportViewSet(ILESBaseViewSet, viewsets.ReadOnlyModelViewSet):
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    permission_classes = [ReportPermission]
    search_fields = ("report_definition__name", "status", "output_format")
    ordering = ("-created_at",)

    def get_queryset(self):
        qs = super(ILESBaseViewSet, self).get_queryset()
        return qs.select_related("report_definition", "generated_by")