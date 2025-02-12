from cards.admin import (CodeBatchResource, NFCCardInline,
                         PurchasingCodeInline, URLBatchResource)
from django.contrib import admin, messages
from .models import CodeBatchArchived, URLBatchArchived
from core.mixins import ExportWithInlineMixin

def unarchive_selected(modeladmin, request, queryset):
    queryset.update(archive=False)
    messages.success(request, "Selected records have been un archived.")


@admin.register(URLBatchArchived)
class URLBatchArchivedAdmin(ExportWithInlineMixin, admin.ModelAdmin):
    resource_class = URLBatchResource
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [NFCCardInline]
    actions = [unarchive_selected, 'export_selected_records']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False


@admin.register(CodeBatchArchived)
class CodeBatchArchivedAdmin(ExportWithInlineMixin, admin.ModelAdmin):
    resource_class = CodeBatchResource
    list_display = ["count", "created_at", "user"]
    readonly_fields = ["user"]
    inlines = [PurchasingCodeInline]
    actions = [unarchive_selected, 'export_selected_records']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=True)

    def has_add_permission(self, request):
        return False
