from __future__ import annotations
from typing import Any
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
    Company,
    InternshipPlacement,
    SupervisorAssignment,
    WeeklyLog,
    Feedback,
    EvaluationCriterion,
    Evaluation,
    EvaluationScore,
    FinalResult,
    AuditLog,
    ReportDefinition,
    GeneratedReport,
)

# ============================================================
# COMPANY ADMIN
# ============================================================

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_name", "location", "contact_person_name", "contact_email", "created_at")
    list_filter = ("location",)
    search_fields = ("company_name", "location", "contact_email", "contact_person_name")
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        (_("Core Information"), {
            "fields": ("company_name", "location", "website")
        }),
        (_("Contact Details"), {
            "fields": ("contact_person_name", "contact_email", "contact_phone")
        }),
        (_("Metadata"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

# ============================================================
# INLINES
# ============================================================

class SupervisorAssignmentInline(admin.TabularInline):
    model = SupervisorAssignment
    extra = 0
    fields = ("supervisor", "assignment_role", "is_active")
    autocomplete_fields = ("supervisor",)
    show_change_link = True

class WeeklyLogInline(admin.TabularInline):
    model = WeeklyLog
    extra = 0
    fields = ("week_number", "title", "status", "submitted_at")
    readonly_fields = ("submitted_at",)
    show_change_link = True

class EvaluationScoreInline(admin.TabularInline):
    model = EvaluationScore
    extra = 0
    fields = ("criterion", "raw_score", "weight_percent", "weighted_score")
    readonly_fields = ("weighted_score",)
    autocomplete_fields = ("criterion",)

    def has_delete_permission(self, request: Any, obj: Any = None) -> bool:
        if obj and getattr(obj, "status", None) != "DRAFT":
            return False
        return super().has_delete_permission(request, obj)

# ============================================================
# PLACEMENT & ASSIGNMENT ADMIN
# ============================================================

@admin.register(InternshipPlacement)
class InternshipPlacementAdmin(admin.ModelAdmin):
    list_display = ("student", "company", "start_date", "end_date", "status", "approved_by")
    list_filter = ("status", "start_date", "company")
    search_fields = ("student__user__username", "student__registration_number", "company__company_name")
    readonly_fields = ("created_at", "updated_at", "requested_at", "approved_at")
    date_hierarchy = "start_date"
    autocomplete_fields = ("student", "company", "approved_by")
    inlines = [SupervisorAssignmentInline, WeeklyLogInline]
    actions = ["approve_placements", "reject_placements"]

    fieldsets = (
        (_("Placement Details"), {
            "fields": ("student", "company", "org_department")
        }),
        (_("Timeline & Status"), {
            "fields": ("start_date", "end_date", "status", "rejection_reason")
        }),
        (_("Approval Data"), {
            "fields": ("approved_by", "requested_at", "approved_at"),
            "classes": ("collapse",)
        }),
    )

    @admin.action(description=_("Approve selected placements"))
    def approve_placements(self, request, queryset):
        updated = queryset.update(status="APPROVED", approved_at=timezone.now())
        self.message_user(request, ngettext(
            "%d placement was successfully approved.",
            "%d placements were successfully approved.",
            updated,
        ) % updated, messages.SUCCESS)

    @admin.action(description=_("Reject selected placements"))
    def reject_placements(self, request, queryset):
        updated = queryset.update(status="REJECTED")
        self.message_user(request, f"{updated} placements rejected.", messages.WARNING)

    def get_queryset(self, request: Any) -> QuerySet:
        return super().get_queryset(request).select_related("student__user", "company", "approved_by").prefetch_related("assignments", "logs")

@admin.register(SupervisorAssignment)
class SupervisorAssignmentAdmin(admin.ModelAdmin):
    list_display = ("placement", "supervisor", "assignment_role", "is_active")
    list_filter = ("assignment_role", "is_active")
    search_fields = ("placement__student__user__username", "supervisor__user__username")
    autocomplete_fields = ("placement", "supervisor")

    def get_queryset(self, request: Any) -> QuerySet:
        return super().get_queryset(request).select_related("placement__student", "supervisor__user")

# ============================================================
# LOGS & FEEDBACK
# ============================================================

class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    fields = ("supervisor", "decision", "comment", "is_latest")
    show_change_link = True

@admin.register(WeeklyLog)
class WeeklyLogAdmin(admin.ModelAdmin):
    list_display = ("placement", "week_number", "status", "submitted_at")
    list_filter = ("status", "week_number")
    search_fields = ("placement__student__user__username", "title")
    autocomplete_fields = ("placement",)
    inlines = [FeedbackInline]

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("weekly_log", "supervisor", "decision", "is_latest")
    list_filter = ("decision", "is_latest")
    autocomplete_fields = ("weekly_log", "supervisor")

# ============================================================
# EVALUATIONS & RESULTS
# ============================================================

@admin.register(EvaluationCriterion)
class EvaluationCriterionAdmin(admin.ModelAdmin):
    list_display = ("criterion_name", "criterion_group", "weight_percent", "is_active")
    list_filter = ("criterion_group", "is_active")
    search_fields = ("criterion_name",)

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("placement", "evaluator", "evaluation_type", "total_score", "status")
    list_filter = ("evaluation_type", "status")
    readonly_fields = ("total_score", "weighted_score", "created_at")
    autocomplete_fields = ("placement", "evaluator")
    inlines = [EvaluationScoreInline]
    actions = ["recalculate_selected_evaluations"]

    @admin.action(description=_("Recalculate scores for selected evaluations"))
    def recalculate_selected_evaluations(self, request, queryset):
        count = 0
        for evaluation in queryset:
            evaluation.recalculate_and_sync()
            count += 1
        self.message_user(request, f"Successfully recalculated {count} evaluations.", messages.SUCCESS)

    def get_queryset(self, request: Any) -> QuerySet:
        return super().get_queryset(request).select_related("placement__student", "evaluator__user")

@admin.register(FinalResult)
class FinalResultAdmin(admin.ModelAdmin):
    list_display = ("placement", "final_mark", "published_by")
    readonly_fields = ("final_mark", "created_at")
    autocomplete_fields = ("placement",)
    
    fieldsets = (
        (_("Target"), {
            "fields": ("placement",)
        }),
        (_("Component Scores"), {
            "fields": ("weekly_logs_score", "supervisor_evaluation_score", "final_report_score", "workplace_assessment_score")
        }),
        (_("Final Output"), {
            "fields": ("final_mark", "published_by")
        }),
    )

# ============================================================
# IMMUTABLE SYSTEM LOGS (STRICTLY READ-ONLY)
# ============================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "model_label", "created_at")
    list_filter = ("action", "model_label")
    search_fields = ("actor__username", "model_label")
    readonly_fields = [f.name for f in AuditLog._meta.fields] # Make ALL fields read-only
    
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ReportDefinition)
class ReportDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "report_type", "frequency", "is_active")
    list_filter = ("report_type", "frequency", "is_active")
    search_fields = ("name",)

@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ("report_definition", "generated_by", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = [f.name for f in GeneratedReport._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

# Global admin configurations
admin.site.site_header = _("ILES1 Administration")
admin.site.site_title = _("ILES1 Admin Portal")
admin.site.index_title = _("System Management")