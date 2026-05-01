import uuid
from decimal import Decimal
from datetime import date, datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from users.models import (
    StudentProfile,
    SupervisorProfile,
    SupervisorType,
    AdministratorProfile,
)

# ============================================================
# UTILITIES & SERIALIZATION
# ============================================================

def make_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, models.Model):
        return str(value.pk)
    if isinstance(value, dict):
        return {str(k): make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]
    return value

# ============================================================
# ABSTRACT BASE MODELS
# ============================================================

class ILESBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ============================================================
# CORE ENTITIES & MANAGERS
# ============================================================

class PlacementQuerySet(models.QuerySet):
    def active(self):
        today = timezone.now().date()
        return self.filter(status="IN_PROGRESS", start_date__lte=today, end_date__gte=today)

    def by_student(self, student_reg):
        return self.filter(student__registration_number=student_reg)

class Company(ILESBaseModel):
    company_name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    contact_person_name = models.CharField(max_length=150, blank=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["company_name"]

    def __str__(self):
        return self.company_name

class PlacementStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    IN_PROGRESS = "IN_PROGRESS", _("In Progress")
    COMPLETED = "COMPLETED", _("Completed")
    CANCELLED = "CANCELLED", _("Cancelled")

class InternshipPlacement(ILESBaseModel):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="placements")
    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="placements")
    
    org_department = models.CharField(max_length=150, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=PlacementStatus.choices, default=PlacementStatus.PENDING)
    
    # Missing fields required by views/admin added here:
    requested_at = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(AdministratorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    objects = PlacementQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status", "start_date"])]

    def clean(self):
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(_("Start date must precede end date."))

    @property
    def duration_weeks(self):
        delta = self.end_date - self.start_date
        return max(1, delta.days // 7)

    def __str__(self):
        return f"{self.student.registration_number} @ {self.company.company_name}"

# ============================================================
# SUPERVISION & LOGS
# ============================================================

class AssignmentRole(models.TextChoices):
    ACADEMIC = "ACADEMIC", _("Academic Supervisor")
    WORKPLACE = "WORKPLACE", _("Workplace Supervisor")

class SupervisorAssignment(ILESBaseModel):
    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name="assignments")
    supervisor = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE, related_name="active_placements")
    assignment_role = models.CharField(max_length=20, choices=AssignmentRole.choices)
    is_active = models.BooleanField(default=True)
    
    # Missing fields required by views added here:
    assigned_by = models.ForeignKey(AdministratorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["placement", "assignment_role"], condition=Q(is_active=True), name="one_active_supervisor_per_role")
        ]

    def clean(self):
        if self.supervisor.supervisor_type != self.assignment_role:
            raise ValidationError(_("Supervisor specialty does not match assignment role."))

class WeeklyLogStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    SUBMITTED = "SUBMITTED", _("Submitted")
    REVIEWED = "REVIEWED", _("Reviewed")

class WeeklyLog(ILESBaseModel):
    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name="logs")
    week_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(52)])
    title = models.CharField(max_length=200)
    activities = models.TextField()
    status = models.CharField(max_length=20, choices=WeeklyLogStatus.choices, default=WeeklyLogStatus.DRAFT)
    
    # Missing field required by views added here:
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("placement", "week_number")

class FeedbackDecision(models.TextChoices):
    COMMENT = "COMMENT", _("Comment")
    APPROVED = "APPROVED", _("Approved")
    REVISION_REQUIRED = "REVISION_REQUIRED", _("Revision Required")

class Feedback(ILESBaseModel):
    weekly_log = models.ForeignKey(WeeklyLog, on_delete=models.CASCADE, related_name="feedback_entries")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True) 
    decision = models.CharField(max_length=30, choices=FeedbackDecision.choices, default=FeedbackDecision.COMMENT)
    comment = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Feedback on {self.weekly_log.title}: {self.decision}"

# ============================================================
# ADVANCED EVALUATION ENGINE
# ============================================================

class EvaluationCriterion(ILESBaseModel):
    criterion_name = models.CharField(max_length=255)
    criterion_group = models.CharField(max_length=100, help_text="e.g., SUPERVISOR_EVALUATION, WORKPLACE_ASSESSMENT")
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["criterion_group", "criterion_name"]
        verbose_name_plural = "Evaluation Criteria"

    def __str__(self):
        return f"{self.criterion_name} [{self.criterion_group}] ({self.weight_percent}%)"

class EvaluationType(models.TextChoices):
    ACADEMIC = "ACADEMIC_EVALUATION", _("Academic Evaluation")
    WORKPLACE = "WORKPLACE_ASSESSMENT", _("Workplace Assessment")
    FINAL_REPORT = "FINAL_REPORT", _("Final Report")
    LOG_SUMMARY = "WEEKLY_LOG_SUMMARY", _("Weekly Log Summary")

class EvaluationStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    PENDING = "PENDING", _("Pending")
    SUBMITTED = "SUBMITTED", _("Submitted")
    COMPLETED = "COMPLETED", _("Completed")

class Evaluation(ILESBaseModel):
    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name="evaluations")
    evaluator = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE)
    evaluation_type = models.CharField(max_length=30, choices=EvaluationType.choices)
    
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    weighted_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=EvaluationStatus.choices, default=EvaluationStatus.DRAFT)
    
    # Missing field required by views added here:
    submitted_at = models.DateTimeField(null=True, blank=True)

    @transaction.atomic
    def recalculate_and_sync(self):
        scores = self.scores.all()
        self.total_score = sum(s.raw_score for s in scores)
        self.weighted_score = sum(s.weighted_score for s in scores)
        self.save()

        final, _ = FinalResult.objects.get_or_create(placement=self.placement)
        mapping = {
            EvaluationType.ACADEMIC: 'supervisor_evaluation_score',
            EvaluationType.WORKPLACE: 'workplace_assessment_score',
            EvaluationType.LOG_SUMMARY: 'weekly_logs_score',
            EvaluationType.FINAL_REPORT: 'final_report_score',
        }
        setattr(final, mapping[self.evaluation_type], self.weighted_score)
        final.save()

class EvaluationScore(ILESBaseModel):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey(EvaluationCriterion, on_delete=models.CASCADE)
    raw_score = models.DecimalField(max_digits=5, decimal_places=2)
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2)
    weighted_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.weighted_score = (self.raw_score * self.weight_percent) / Decimal("100.00")
        super().save(*args, **kwargs)

# ============================================================
# FINAL RESULTS, AUDIT & REPORTING
# ============================================================

class FinalResult(ILESBaseModel):
    placement = models.OneToOneField(InternshipPlacement, on_delete=models.CASCADE, related_name="final_result")
    weekly_logs_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    supervisor_evaluation_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    final_report_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    workplace_assessment_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    final_mark = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    
    # Missing fields required by views added here:
    published_by = models.ForeignKey(AdministratorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.final_mark = (
            self.weekly_logs_score + 
            self.supervisor_evaluation_score + 
            self.final_report_score + 
            self.workplace_assessment_score
        )
        super().save(*args, **kwargs)

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)
    model_label = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    changes = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.changes = make_json_safe(self.changes)
        super().save(*args, **kwargs)

# Missing Reporting Models added here:
class ReportStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    COMPLETED = "COMPLETED", _("Completed")
    FAILED = "FAILED", _("Failed")

class ReportDefinition(ILESBaseModel):
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=100)
    frequency = models.CharField(max_length=50)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class GeneratedReport(ILESBaseModel):
    report_definition = models.ForeignKey(ReportDefinition, on_delete=models.CASCADE)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING)
    output_format = models.CharField(max_length=10, default="PDF")
    summary = models.JSONField(default=dict)
    generated_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.summary = make_json_safe(self.summary)
        super().save(*args, **kwargs)