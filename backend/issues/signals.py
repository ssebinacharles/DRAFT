from __future__ import annotations

from typing import Any, Dict
from datetime import datetime, date
from decimal import Decimal
import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    AuditLog,
    WeeklyLog,
    Feedback,
    EvaluationScore,
    Evaluation,
    FinalResult,
)

# ============================================================
# AUDIT LOGGING ENGINE
# ============================================================

def _model_label(instance: models.Model) -> str:
    """Returns the standardized app_label.model_name format."""
    return f"{instance._meta.app_label}.{instance._meta.object_name}"

def _capture_snapshot(instance: models.Model) -> Dict[str, Any]:
    """
    Captures the raw database values of an instance.
    Uses `attname` to get raw IDs for ForeignKeys rather than 
    triggering N+1 queries by fetching the related objects.
    """
    snapshot: Dict[str, Any] = {}
    for field in instance._meta.fields:
        # Use attname (e.g., 'student_id') instead of name ('student')
        val = getattr(instance, field.attname)
        
        # Convert non-serializable types to strings for safe comparison
        if isinstance(val, (datetime, date)):
            val = val.isoformat()
        elif isinstance(val, (Decimal, uuid.UUID)):
            val = str(val)
            
        snapshot[field.name] = val
    return snapshot

@receiver(pre_save)
def capture_pre_save_snapshot(sender: type[models.Model], instance: models.Model, **kwargs: Any) -> None:
    """Stores the state of the object exactly before it is saved."""
    if not isinstance(instance, models.Model) or instance._meta.app_label != "issues":
        return
    if isinstance(instance, AuditLog):
        return
        
    if instance.pk:
        try:
            # Fetch the clean state from the database to ensure accuracy
            db_instance = sender.objects.get(pk=instance.pk)
            instance._pre_save_snapshot = _capture_snapshot(db_instance)
        except sender.DoesNotExist:
            instance._pre_save_snapshot = {}
    else:
        instance._pre_save_snapshot = {}

@receiver(post_save)
def create_audit_log_on_save(sender: type[models.Model], instance: models.Model, created: bool, **kwargs: Any) -> None:
    """Generates the AuditLog by diffing the pre_save snapshot with the new state."""
    if not isinstance(instance, models.Model) or instance._meta.app_label != "issues":
        return
    if isinstance(instance, AuditLog):
        return

    action = "CREATE" if created else "UPDATE"
    changes: Dict[str, Any] = {}
    
    old_state = getattr(instance, "_pre_save_snapshot", {})
    new_state = _capture_snapshot(instance)

    if not created:
        for field_name, old_value in old_state.items():
            new_value = new_state.get(field_name)
            if new_value != old_value:
                changes[field_name] = {"from": old_value, "to": new_value}
        
        # If it's an update but no tracked fields changed, abort logging
        if not changes:
            return

    AuditLog.objects.create(
        actor=getattr(instance, "updated_by", None), # Requires middleware to set this
        action=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=str(instance.pk),
        model_label=_model_label(instance),
        changes=changes,
    )

@receiver(post_delete)
def create_audit_log_on_delete(sender: type[models.Model], instance: models.Model, **kwargs: Any) -> None:
    """Logs the deletion of any tracked model."""
    if not isinstance(instance, models.Model) or instance._meta.app_label != "issues":
        return
    if isinstance(instance, AuditLog):
        return

    AuditLog.objects.create(
        actor=getattr(instance, "updated_by", None),
        action="DELETE",
        content_type=ContentType.objects.get_for_model(instance),
        object_id=str(instance.pk),
        model_label=_model_label(instance),
        changes=_capture_snapshot(instance), # Store the final state as the change
    )

# ============================================================
# BUSINESS LOGIC SIGNALS
# ============================================================

@receiver(post_save, sender=Feedback)
def update_feedback_latest(sender: type[Feedback], instance: Feedback, created: bool, **kwargs: Any) -> None:
    """
    Ensures only one piece of feedback per log is marked as 'latest'.
    Wrapped in an atomic transaction to prevent race conditions.
    """
    if created and instance.is_latest:
        with transaction.atomic():
            Feedback.objects.filter(
                weekly_log=instance.weekly_log
            ).exclude(pk=instance.pk).update(is_latest=False)

@receiver(post_save, sender=EvaluationScore)
@receiver(post_delete, sender=EvaluationScore)
def recalculate_evaluation_totals(sender: type[EvaluationScore], instance: EvaluationScore, **kwargs: Any) -> None:
    """
    Triggers the parent Evaluation to recalculate its totals 
    when a child EvaluationScore is created, updated, or deleted.
    """
    evaluation = instance.evaluation
    try:
        # Relies on the transactional method we built in models.py
        evaluation.recalculate_and_sync() 
    except Exception as e:
        # In production, log this exception
        pass

@receiver(pre_save, sender=FinalResult)
def recalculate_final_mark(sender: type[FinalResult], instance: FinalResult, **kwargs: Any) -> None:
    """
    CRITICAL FIX: Moved from post_save to pre_save.
    Modifying own fields in post_save causes infinite recursion loops.
    """
    try:
        # Relies on the recalculate logic built into the model
        instance.final_mark = (
            instance.weekly_logs_score +
            instance.supervisor_evaluation_score +
            instance.final_report_score +
            instance.workplace_assessment_score
        )
    except Exception:
        pass

@receiver(pre_save, sender=WeeklyLog)
def set_submitted_timestamp(sender: type[WeeklyLog], instance: WeeklyLog, **kwargs: Any) -> None:
    """Automatically stamps the log when transitioned to SUBMITTED."""
    if instance.status == "SUBMITTED" and not instance.submitted_at:
        
        old_status = None
        if instance.pk:
            old_state = getattr(instance, "_pre_save_snapshot", {})
            old_status = old_state.get("status")

        if old_status != "SUBMITTED":
            instance.submitted_at = timezone.now()