from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from core.mixins import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource
from import_export.widgets import ManyToManyWidget
from cards.models import NFCCard
from core.mixins import ExportMixin
from .forms import CustomUserChangeForm, CustomUserCreationForm

User = get_user_model()

class CustomManyToManyWidget(ManyToManyWidget):
    def render(self, value, obj=None):
        if value:
            return "\n".join([str(item) for item in value.all()])
        return ""


class UserResource(ModelResource):
    cards = Field(
        column_name="Cards",
        attribute="user_cards",
        widget=CustomManyToManyWidget(NFCCard, field="uuid"),
    )

    class Meta:
        fields = ("username", "email", "cards", "first_name", "last_name", "role")
        export_order = ("username", "email", "cards", "first_name", "last_name", "role")
        model = User


@admin.register(User)
class CustomUserAdmin(ExportMixin, UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    resource_class = UserResource
    actions = ["export_selected_records"]
    list_display = [
        "__str__",
        "email",
        "username",
        "role",
    ]
    list_filter = ["role"]
    fieldsets = (
        ("Login info", {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "image")}),
        ("Contact info", {"fields": ("email",)}),
        (
            "Permissions",
            {"fields": ("role", "is_active",)},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "role",
                    "image",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = ("email", "username")
    ordering = ("email",)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        user = User.objects.get(pk=object_id)
        if user.is_superuser and not request.user.is_superuser:
            raise PermissionDenied(
                "You do not have permission to edit superuser accounts."
            )
        return super().change_view(request, object_id, form_url, extra_context)

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if obj == request.user and "is_superuser" in form.changed_data:
            raise PermissionDenied("You cannot change your own superuser status.")
        if not request.user.is_superuser and "is_superuser" in form.changed_data:
            raise PermissionDenied(
                "You do not have permission to edit superuser status."
            )
        if obj.pk == 1:
            if "is_superuser" in form.changed_data and "is_superuser" not in form.data:
                raise PermissionDenied(
                    "You cannot change superuser status for this account."
                )
            if "is_staff" in form.changed_data and "is_staff" not in form.data:
                raise PermissionDenied(
                    "You cannot change staff status for this account."
                )
        super().save_model(request, obj, form, change)
