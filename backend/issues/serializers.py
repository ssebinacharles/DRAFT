from __future__ import annotations
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet
from rest_framework import serializers

from users.models import (
    User,
    UserRole,
    StudentProfile,
    SupervisorProfile,
    AdministratorProfile,
)

from .models import (
    AuditLog,
    Company,
    Evaluation,
    EvaluationCriterion,
    EvaluationScore,
    Feedback,
    FinalResult,
    GeneratedReport,
    InternshipPlacement,
    ReportDefinition,
    SupervisorAssignment,
    WeeklyLog,
)

# ============================================================
# ADVANCED BASE CLASSES & MIXINS
# ============================================================

class ILESBaseSerializer(serializers.ModelSerializer):
    """
    Enterprise Base Serializer combining Model full_clean() validation
    with Dynamic Field selection for GraphQL-like payload reduction.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Instantiate the superclass normally
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        # Drop any fields that are not specified in the `fields` argument
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def _run_model_validation(self, instance: Any) -> None:
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise serializers.ValidationError(exc.message_dict)
            raise serializers.ValidationError(exc.messages)

    def create(self, validated_data: dict) -> Any:
        model = self.Meta.model
        # Pop many-to-many or reverse relations if any exist before instantiation
        instance = model(**validated_data)
        self._run_model_validation(instance)
        return super().create(validated_data)

    def update(self, instance: Any, validated_data: dict) -> Any:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        self._run_model_validation(instance)
        return super().update(instance, validated_data)

# ============================================================
# USER / PROFILE SUMMARY SERIALIZERS
# ============================================================

class UserSummarySerializer(ILESBaseSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "role")

class StudentProfileSummarySerializer(ILESBaseSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ("id", "user", "registration_number", "course", "year_of_study", "department")

class SupervisorProfileSummarySerializer(ILESBaseSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = SupervisorProfile
        fields = ("id", "user", "supervisor_type", "organization_name", "title")

class AdministratorProfileSummarySerializer(ILESBaseSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = AdministratorProfile
        fields = ("id", "user", "office_name")

# ============================================================
# COMPANY
# ============================================================

class CompanySerializer(ILESBaseSerializer):
    class Meta:
        model = Company
        fields = (
            "id", "company_name", "location", "contact_email", 
            "contact_phone", "website", "contact_person_name", 
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

class CompanySummarySerializer(ILESBaseSerializer):
    class Meta:
        model = Company
        fields = ("id", "company_name", "location")

# ============================================================
# INTERNSHIP PLACEMENT & ASSIGNMENT
# ============================================================

class SupervisorAssignmentSummarySerializer(ILESBaseSerializer):
    supervisor = SupervisorProfileSummarySerializer(read_only=True)

    class Meta:
        model = SupervisorAssignment
        fields = ("id", "supervisor", "assignment_role", "assigned_at", "is_active")

class SupervisorAssignmentSerializer(ILESBaseSerializer):
    placement_id = serializers.PrimaryKeyRelatedField(source="placement", queryset=InternshipPlacement.objects.all(), write_only=True)
    supervisor_id = serializers.PrimaryKeyRelatedField(source="supervisor", queryset=SupervisorProfile.objects.all(), write_only=True)
    assigned_by_id = serializers.PrimaryKeyRelatedField(source="assigned_by", queryset=AdministratorProfile.objects.all(), write_only=True, required=False, allow_null=True)
    
    supervisor = SupervisorProfileSummarySerializer(read_only=True)
    assigned_by = AdministratorProfileSummarySerializer(read_only=True)

    class Meta:
        model = SupervisorAssignment
        fields = (
            "id", "placement_id", "supervisor", "supervisor_id", "assigned_by", 
            "assigned_by_id", "assignment_role", "assigned_at", "is_active", 
            "created_at", "updated_at"
        )
        read_only_fields = ("id", "assigned_at", "created_at", "updated_at")

class InternshipPlacementSerializer(ILESBaseSerializer):
    # Read-only nested representations
    student = StudentProfileSummarySerializer(read_only=True)
    company = CompanySummarySerializer(read_only=True)
    approved_by = AdministratorProfileSummarySerializer(read_only=True)
    supervisor_assignments = SupervisorAssignmentSummarySerializer(many=True, read_only=True)

    # Write-only ID mappings
    student_id = serializers.PrimaryKeyRelatedField(source="student", queryset=StudentProfile.objects.all(), write_only=True, required=False)
    company_id = serializers.PrimaryKeyRelatedField(source="company", queryset=Company.objects.all(), write_only=True)
    approved_by_id = serializers.PrimaryKeyRelatedField(source="approved_by", queryset=AdministratorProfile.objects.all(), write_only=True, required=False, allow_null=True)

    class Meta:
        model = InternshipPlacement
        fields = (
            "id", "student", "student_id", "company", "company_id", 
            "approved_by", "approved_by_id", "org_department", 
            "start_date", "end_date", "status", "requested_at", 
            "approved_at", "rejection_reason", "supervisor_assignments", 
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "requested_at", "approved_at", "created_at", "updated_at")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        """
        Optimization Method: Views should call this on their queryset to 
        prevent N+1 queries when utilizing this complex nested serializer.
        """
        return queryset.select_related(
            "student__user", 
            "company", 
            "approved_by__user"
        ).prefetch_related(
            "assignments__supervisor__user"
        )

# ============================================================
# WEEKLY LOG + FEEDBACK
# ============================================================

class FeedbackSerializer(ILESBaseSerializer):
    weekly_log_id = serializers.PrimaryKeyRelatedField(source="weekly_log", queryset=WeeklyLog.objects.all(), write_only=True)
    supervisor_id = serializers.PrimaryKeyRelatedField(source="supervisor", queryset=SupervisorProfile.objects.all(), write_only=True, required=False)
    supervisor = SupervisorProfileSummarySerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id", "weekly_log_id", "supervisor", "supervisor_id", 
            "decision", "comment", "is_latest", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

class WeeklyLogSerializer(ILESBaseSerializer):
    placement_id = serializers.PrimaryKeyRelatedField(source="placement", queryset=InternshipPlacement.objects.all(), write_only=True)
    feedback_entries = FeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = WeeklyLog
        fields = (
            "id", "placement_id", "week_number", "title", "activities", 
            "challenges", "lessons_learned", "status", "submitted_at", 
            "feedback_entries", "created_at", "updated_at"
        )
        read_only_fields = ("id", "submitted_at", "created_at", "updated_at")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        return queryset.prefetch_related("feedback_entries__supervisor__user")

# ============================================================
# EVALUATION CRITERIA + SCORES
# ============================================================

class EvaluationCriterionSerializer(ILESBaseSerializer):
    class Meta:
        model = EvaluationCriterion
        fields = ("id", "criterion_name", "criterion_group", "weight_percent", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

class EvaluationScoreSerializer(ILESBaseSerializer):
    criterion_id = serializers.PrimaryKeyRelatedField(source="criterion", queryset=EvaluationCriterion.objects.all(), write_only=True)
    evaluation_id = serializers.PrimaryKeyRelatedField(source="evaluation", queryset=Evaluation.objects.all(), write_only=True)
    criterion = EvaluationCriterionSerializer(read_only=True)

    class Meta:
        model = EvaluationScore
        fields = ("id", "evaluation_id", "criterion", "criterion_id", "raw_score", "weighted_score", "created_at", "updated_at")
        read_only_fields = ("id", "weighted_score", "created_at", "updated_at")

class EvaluationSerializer(ILESBaseSerializer):
    placement_id = serializers.PrimaryKeyRelatedField(source="placement", queryset=InternshipPlacement.objects.all(), write_only=True)
    evaluator_id = serializers.PrimaryKeyRelatedField(source="evaluator", queryset=SupervisorProfile.objects.all(), write_only=True, required=False)
    
    evaluator = SupervisorProfileSummarySerializer(read_only=True)
    scores = EvaluationScoreSerializer(many=True, read_only=True)

    class Meta:
        model = Evaluation
        fields = (
            "id", "placement_id", "evaluator", "evaluator_id", 
            "evaluation_type", "total_score", "weighted_score", 
            "remarks", "status", "submitted_at", "scores", 
            "created_at", "updated_at"
        )
        read_only_fields = ("id", "total_score", "weighted_score", "submitted_at", "created_at", "updated_at")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        return queryset.select_related("evaluator__user").prefetch_related("scores__criterion")

# ============================================================
# FINAL RESULT
# ============================================================

class FinalResultSerializer(ILESBaseSerializer):
    placement_id = serializers.PrimaryKeyRelatedField(source="placement", queryset=InternshipPlacement.objects.all(), write_only=True)
    published_by_id = serializers.PrimaryKeyRelatedField(source="published_by", queryset=AdministratorProfile.objects.all(), write_only=True, required=False, allow_null=True)
    
    published_by = AdministratorProfileSummarySerializer(read_only=True)

    class Meta:
        model = FinalResult
        fields = (
            "id", "placement_id", "published_by", "published_by_id", 
            "weekly_logs_score", "supervisor_evaluation_score", 
            "final_report_score", "workplace_assessment_score", 
            "final_mark", "published_at", "created_at", "updated_at"
        )
        read_only_fields = ("id", "final_mark", "published_at", "created_at", "updated_at")

# ============================================================
# AUDIT LOG & REPORTING
# ============================================================

class AuditLogSerializer(ILESBaseSerializer):
    actor = UserSummarySerializer(read_only=True)
    content_type_display = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = (
            "id", "actor", "action", "content_type_display", "object_id", 
            "model_label", "changes", "ip_address", "created_at"
        )
        read_only_fields = ("id", "created_at")

    def get_content_type_display(self, obj: Any) -> str:
        return str(obj.content_type)

class ReportDefinitionSerializer(ILESBaseSerializer):
    created_by_id = serializers.PrimaryKeyRelatedField(source="created_by", queryset=User.objects.filter(role=UserRole.ADMINISTRATOR), write_only=True, required=False, allow_null=True)
    created_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = ReportDefinition
        fields = (
            "id", "name", "report_type", "frequency", "filters", 
            "is_active", "next_run_at", "last_run_at", "created_by", 
            "created_by_id", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

class GeneratedReportSerializer(ILESBaseSerializer):
    report_definition_id = serializers.PrimaryKeyRelatedField(source="report_definition", queryset=ReportDefinition.objects.all(), write_only=True)
    generated_by_id = serializers.PrimaryKeyRelatedField(source="generated_by", queryset=User.objects.filter(role=UserRole.ADMINISTRATOR), write_only=True, required=False, allow_null=True)
    
    report_definition = ReportDefinitionSerializer(read_only=True)
    generated_by = UserSummarySerializer(read_only=True)

    class Meta:
        model = GeneratedReport
        fields = (
            "id", "report_definition", "report_definition_id", "generated_by", 
            "generated_by_id", "status", "output_format", "output_path", 
            "summary", "generated_at", "created_at", "updated_at"
        )
        read_only_fields = ("id", "generated_at", "created_at", "updated_at")