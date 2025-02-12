from django.contrib import admin
from core.mixins import ExportMixin, DataSetMixin

from .forms import ProductGroupForm
from .models import CRUDLog, LinkDuration, ProductGroup


class ProductGroupResource(DataSetMixin):

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []
        for group in queryset:
            created_at = group.created_at.strftime('%Y-%m-%d, %H:%M %p')
            last_updated = group.updated_at.strftime('%Y-%m-%d, %H:%M %p')
            data.append({
                'Title': str(group),
                'Products': group.get_products_display(),
                'Created At': created_at,
                "Last Updated": last_updated,
            })

        headers = ['Title', "Products", 'Created At', 'Last Updated']
        dataset = self._create_dataset(data, headers)

        return dataset


@admin.register(ProductGroup)
class ProductGroupAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "get_products_display", "created_at", "updated_at"]
    resource_class = ProductGroupResource
    form = ProductGroupForm
    actions = ["export_selected_records"]

    def get_products_display(self, obj):
        return obj.get_products_display()

    get_products_display.short_description = "Products"


@admin.register(LinkDuration)
class LinkDurationAdmin(admin.ModelAdmin):
    list_display = ["__str__"]


class CRUDLogResource(DataSetMixin):

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []
        for log in queryset:
            timestamp = log.timestamp.strftime('%Y-%m-%d, %H:%M %p')
            data.append({
                'Message': str(log),
                'Action': log.get_action_display(),
                'Object Name': log.object_name,
                'User': log.user.username if log.user else 'No User connected',
                'Created At': timestamp,
            })

        headers = ['Message', "Action", 'Object Name', 'User', 'Created At']
        dataset = self._create_dataset(data, headers)

        return dataset


@admin.register(CRUDLog)
class CRUDLogAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = CRUDLogResource
    list_display = ['__str__', 'action', 'object_name', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['object_name', 'user__username']
    actions = ["export_selected_records"]

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        return self.fields or [f.name for f in self.model._meta.fields]
