from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _, ngettext

from .models import (
    User,
    UserRole,
    StudentProfile,
    SupervisorProfile,
    AdministratorProfile,
)

# ============================================================
# DYNAMIC INLINES
# ============================================================

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = _("Student Profile Data")
    fk_name = "user"
    readonly_fields = ("id", "created_at", "updated_at")
    classes = ("collapse",)

class SupervisorProfileInline(admin.StackedInline):
    model = SupervisorProfile
    can_delete = False
    verbose_name_plural = _("Supervisor Profile Data")
    fk_name = "user"
    readonly_fields = ("id", "created_at", "updated_at")
    classes = ("collapse",)

class AdministratorProfileInline(admin.StackedInline):
    model = AdministratorProfile
    can_delete = False
    verbose_name_plural = _("Administrator Profile Data")
    fk_name = "user"
    readonly_fields = ("id", "created_at", "updated_at")
    classes = ("collapse",)


# ============================================================
# USER ADMIN
# ============================================================

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "get_full_name",
        "role",
        "is_active",
        "is_verified",
    )
    list_filter = ("role", "is_active", "is_verified", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("username",)
    actions = ["verify_selected_users"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "role",
                    "is_verified",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Metadata"), 
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            }
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "role",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    def get_inline_instances(self, request, obj=None):
        """
        Dynamically load the correct profile inline based on the user's role.
        """
        if not obj:
            return []
            
        inlines = []
        if obj.role == UserRole.STUDENT:
            inlines.append(StudentProfileInline(self.model, self.admin_site))
        elif obj.role == UserRole.SUPERVISOR:
            inlines.append(SupervisorProfileInline(self.model, self.admin_site))
        elif obj.role == UserRole.ADMINISTRATOR:
            inlines.append(AdministratorProfileInline(self.model, self.admin_site))
            
        return inlines

    @admin.action(description=_("Mark selected users as verified"))
    def verify_selected_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(
            request,
            ngettext(
                "%d user was successfully verified.",
                "%d users were successfully verified.",
                updated,
            ) % updated,
            messages.SUCCESS,
        )


# ============================================================
# STANDALONE PROFILE ADMINS
# ============================================================

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "registration_number", "course", "year_of_study", "department")
    search_fields = ("user__username", "user__email", "registration_number", "course", "department")
    list_filter = ("course", "department", "year_of_study")
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("user",)  # Prevents massive dropdowns of users


@admin.register(SupervisorProfile)
class SupervisorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "supervisor_type", "organization_name", "title")
    search_fields = ("user__username", "user__email", "organization_name", "title")
    list_filter = ("supervisor_type", "organization_name")
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("user",)


@admin.register(AdministratorProfile)
class AdministratorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "office_name")
    search_fields = ("user__username", "user__email", "office_name")
    readonly_fields = ("id", "created_at", "updated_at")
    autocomplete_fields = ("user",)