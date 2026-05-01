from __future__ import annotations
from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import QuerySet
from rest_framework import serializers

from .models import (
    User,
    UserRole,
    StudentProfile,
    SupervisorProfile,
    AdministratorProfile,
)


# ============================================================
# BASE SERIALIZER (CONSISTENCY WITH ISSUES APP)
# ============================================================

class ILESUserBaseSerializer(serializers.ModelSerializer):
    """
    Base serializer providing Dynamic Field selection and 
    Django Model full_clean() validation on save.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

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
        instance = model(**validated_data)
        self._run_model_validation(instance)
        return super().create(validated_data)

    def update(self, instance: Any, validated_data: dict) -> Any:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        self._run_model_validation(instance)
        return super().update(instance, validated_data)


# ============================================================
# PROFILE SERIALIZERS
# ============================================================

class StudentProfileSerializer(ILESUserBaseSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            "id", "user", "username", "full_name", "registration_number", 
            "course", "year_of_study", "department", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        return queryset.select_related("user")


class SupervisorProfileSerializer(ILESUserBaseSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = SupervisorProfile
        fields = (
            "id", "user", "username", "full_name", "supervisor_type", 
            "organization_name", "title", "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        return queryset.select_related("user")


class AdministratorProfileSerializer(ILESUserBaseSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = AdministratorProfile
        fields = (
            "id", "user", "username", "full_name", "office_name", 
            "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        return queryset.select_related("user")


# ============================================================
# UNIFIED USER SERIALIZER
# ============================================================

class UserSerializer(ILESUserBaseSerializer):
    password = serializers.CharField(write_only=True, required=False)
    # Automatically injects the user's specific profile data
    profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name", 
            "role", "phone_number", "is_verified", "is_staff", 
            "is_active", "password", "profile"
        )
        read_only_fields = ("id", "is_verified", "is_staff", "is_active")

    @classmethod
    def setup_eager_loading(cls, queryset: QuerySet) -> QuerySet:
        """Prefetch all possible profiles so the SerializerMethodField doesn't cause N+1 queries."""
        return queryset.select_related(
            "student_profile", 
            "supervisor_profile", 
            "administrator_profile"
        )

    def get_profile(self, obj: User) -> dict | None:
        """
        Dynamically returns the profile data associated with the user's role.
        Utilizes reverse relations cached by `setup_eager_loading`.
        """
        if obj.role == UserRole.STUDENT and hasattr(obj, 'student_profile'):
            return StudentProfileSerializer(obj.student_profile).data
        
        if obj.role == UserRole.SUPERVISOR and hasattr(obj, 'supervisor_profile'):
            return SupervisorProfileSerializer(obj.supervisor_profile).data
            
        if obj.role == UserRole.ADMINISTRATOR and hasattr(obj, 'administrator_profile'):
            return AdministratorProfileSerializer(obj.administrator_profile).data
            
        return None

    def validate_password(self, value: str) -> str:
        """Enforces Django's secure password validators (length, commonality, etc)."""
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password", None)
        
        # We bypass super().create() here because BaseUserManager handles password hashing
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save()
        return user

    def update(self, instance: User, validated_data: dict) -> User:
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.full_clean()
        instance.save()
        return instance