import uuid
from decimal import Decimal
from datetime import date, datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.db.models import Q, Sum
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
    """
    Advanced recursive serializer. Handles Decimals as strings to 
    preserve precision and UUIDs for database compatibility.
    """
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
    """
    Advanced base with UUIDs to prevent ID scraping and 
    indexed timestamps for performance.
    """
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
    approved_by = models.ForeignKey(AdministratorProfile, on_delete=models.SET_NULL, null=True, blank=True)
    
    org_department = models.CharField(max_length=150, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=PlacementStatus.choices, default=PlacementStatus.PENDING)
    
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

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["placement", "assignment_role"], condition=Q(is_active=True), name="one_active_supervisor_per_role")
        ]

    def clean(self):
        if self.supervisor.supervisor_type != self.assignment_role:
            raise ValidationError(_("Supervisor specialty does not match assignment role."))

class WeeklyLog(ILESBaseModel):
    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name="logs")
    week_number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(52)])
    title = models.CharField(max_length=200)
    activities = models.TextField()
    status = models.CharField(max_length=20, default="DRAFT")

    class Meta:
        unique_together = ("placement", "week_number")

# ============================================================
# ADVANCED EVALUATION ENGINE
# ============================================================

class EvaluationType(models.TextChoices):
    ACADEMIC = "ACADEMIC_EVALUATION", _("Academic Evaluation")
    WORKPLACE = "WORKPLACE_ASSESSMENT", _("Workplace Assessment")
    FINAL_REPORT = "FINAL_REPORT", _("Final Report")
    LOG_SUMMARY = "WEEKLY_LOG_SUMMARY", _("Weekly Log Summary")

class Evaluation(ILESBaseModel):
    placement = models.ForeignKey(InternshipPlacement, on_delete=models.CASCADE, related_name="evaluations")
    evaluator = models.ForeignKey(SupervisorProfile, on_delete=models.CASCADE)
    evaluation_type = models.CharField(max_length=30, choices=EvaluationType.choices)
    
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    weighted_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, default="DRAFT")

    @transaction.atomic
    def recalculate_and_sync(self):
        """Aggregates all criteria scores and updates the FinalResult record."""
        scores = self.scores.all()
        self.total_score = sum(s.raw_score for s in scores)
        self.weighted_score = sum(s.weighted_score for s in scores)
        self.save()

        # Update FinalResult record automatically
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
    raw_score = models.DecimalField(max_digits=5, decimal_places=2)
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2)
    weighted_score = models.DecimalField(max_digits=5, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.weighted_score = (self.raw_score * self.weight_percent) / Decimal("100.00")
        super().save(*args, **kwargs)

# ============================================================
# FINAL RESULTS & AUDIT
# ============================================================

class FinalResult(ILESBaseModel):
    placement = models.OneToOneField(InternshipPlacement, on_delete=models.CASCADE, related_name="final_result")
    weekly_logs_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    supervisor_evaluation_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    final_report_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    workplace_assessment_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    final_mark = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))

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
    changes = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.changes = make_json_safe(self.changes)
        super().save(*args, **kwargs)

# Create your models here.
