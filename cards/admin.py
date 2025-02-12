import uuid

from core.mixins import DataSetMixin, ExportMixin, ExportWithInlineMixin
from django.contrib import admin, messages
from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.db.models import JSONField
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from django_json_widget.widgets import JSONEditorWidget
from settings.models import ProductGroup

from .forms import CodeBulkCreateForm, URLBulkCreateForm
from .models import CodeBatch, NFCCard, PurchasingCode, URLBatch

User = get_user_model()


def archive_selected(modeladmin, request, queryset):
    queryset.update(archive=True)
    messages.success(request, "Selected records have been archived.")


class NFCCardResource(DataSetMixin):

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []
        for card in queryset:
            last_updated = card.updated_at.strftime('%Y-%m-%d, %H:%M %p')
            try:
                card_code = card.card_code
            except PurchasingCode.DoesNotExist:
                card_code = "No Code connected yet"
            data.append({
                'UUID': str(card),
                "Card User": card.user.username
                if card.user
                else "No User connected yet",
                "Card Code": card_code,
                "URL": card.get_url(),
                "Batch": card.batch,
                "Last Updated": last_updated,
            })

        headers = ['UUID', "Card User", "Card Code", "URL", "Batch", "Last Updated"]
        dataset = self._create_dataset(data, headers)

        return dataset


class PurchasingCodeResource(DataSetMixin):

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []
        for code in queryset:
            last_updated = code.updated_at.strftime('%Y-%m-%d, %H:%M %p')
            if code.group:
                product = code.group
            else:
                product = code.get_product_display()
            data.append({
                'Code': str(code),
                "Password": code.password,
                "Duration": code.duration,
                "Product": product,
                "Batch": code.batch,
                "Card": code.card
                if code.card
                else "No Card connected yet",
                'Last Updated': last_updated,
            })

        headers = ['Code', "Password", "Duration", 'Product', 'Batch', "Card", 'Last Updated']
        dataset = self._create_dataset(data, headers)

        return dataset


@admin.register(NFCCard)
class NFCCardAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "get_url", "card_code", "user", "created_at", "updated_at"]
    fields = ["uuid", "user", "data"]
    readonly_fields = ["uuid", "batch"]
    search_fields = ["uuid", "card_code__code"]
    resource_class = NFCCardResource
    actions = ["export_selected_records"]
    formfield_overrides = {
        JSONField: {'widget': JSONEditorWidget},
    }

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        custom_queryset = self.model.objects.filter(
            id__in=[
                obj.id for obj in self.model.objects.all()
                if search_term.lower() in obj.get_url().lower()
            ]
        )
        queryset |= custom_queryset
        return queryset, use_distinct

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(batch__archive=False)

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("create-url-batch/", self.bulk_create_view, name="url_bulk"),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == "POST":
            form = URLBulkCreateForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data["count"]
                user = request.user
                batch = URLBatch.objects.create(count=count, user=user)
                instances = [
                    NFCCard(uuid=uuid.uuid4(), batch=batch) for _ in range(count)
                ]
                NFCCard.objects.bulk_create(instances)

                self.message_user(
                    request, f"Successfully created {count} URLS.", messages.SUCCESS
                )
                return redirect("admin:cards_urlbatch_changelist")

        else:
            form = URLBulkCreateForm()

        extra_context = {
            "title": "Create URL Batch",
            "head_title": "URL Generator",
            "form": form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, "admin/bulk_create_form.html", context)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ["uuid"]
        return self.readonly_fields

    def get_url(self, obj):
        url = obj.get_absolute_url()
        url_button = f'<a href="{ url }">View On Site</a>'
        return mark_safe(url_button)

    get_url.short_description = "URL"


@admin.register(PurchasingCode)
class PurchasingCodeAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ["__str__", "card", "created_at", "updated_at"]
    fields = ["group", "product", "duration", "card", "code", "password"]
    readonly_fields = ["code", "password", "card"]
    search_fields = ["group__title", "product", "duration", "code__uuid"]
    resource_class = PurchasingCodeResource
    actions = ["export_selected_records"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(batch__archive=False)

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("create-code-batch/", self.bulk_create_view, name="code_bulk"),
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == "POST":
            form = CodeBulkCreateForm(request.POST)
            if form.is_valid():
                count = form.cleaned_data["count"]
                product = form.cleaned_data["product"]
                duration = form.cleaned_data["duration"]
                try:
                    group = ProductGroup.objects.get(id=product)
                except ProductGroup.DoesNotExist:
                    group = None
                except ValueError:
                    group = None
                user = request.user
                batch = CodeBatch.objects.create(count=count, user=user)
                if group:
                    instances = []
                    for _ in range(count):
                        instance = PurchasingCode(
                            group=group, duration=duration, batch=batch
                        )
                        instance.generate_code()
                        instances.append(instance)
                else:
                    instances = []
                    for _ in range(count):
                        instance = PurchasingCode(
                            product=product, duration=duration, batch=batch
                        )
                        instance.generate_code()
                        instances.append(instance)
                PurchasingCode.objects.bulk_create(instances)
                self.message_user(
                    request,
                    f"Successfully created {count} Purchasing Codes.",
                    messages.SUCCESS,
                )
                return redirect("admin:cards_codebatch_changelist")

        else:
            form = CodeBulkCreateForm()

        extra_context = {
            "title": "Create Purchasing Code Batch",
            "head_title": "Code Generator",
            "form": form,
        }
        context = {
            **site.each_context(request),
            **extra_context,
        }
        return render(request, "admin/bulk_create_form.html", context)


class NFCCardInline(admin.TabularInline):
    model = NFCCard
    fields = ["get_url"]
    readonly_fields = ["get_url"]
    can_delete = False
    extra = 0
    show_change_link = True

    def get_url(self, instance):
        base_url = "http://127.0.0.1:8000/services/landingPage/"
        url = f"{ base_url }{instance.uuid}/"
        return url

    get_url.short_description = "URL"


class PurchasingCodeInline(admin.TabularInline):
    model = PurchasingCode
    fields = ["card", "password", "code"]
    readonly_fields = ["card", "password", "code"]
    can_delete = False
    extra = 0
    show_change_link = True


class URLBatchResource(DataSetMixin):

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []
        for batch in queryset:
            inline_queryset = NFCCard.objects.filter(batch=batch)
            for card in inline_queryset:
                try:
                    card_code = card.card_code
                except PurchasingCode.DoesNotExist:
                    card_code = "No Code connected yet"
                last_updated = card.updated_at.strftime("%Y-%m-%d, %H:%M %p")
                data.append(
                    {
                        "Batch": str(batch),
                        "Card User": card.user.username
                        if card.user
                        else "No User connected yet",
                        "Card UUID": card.uuid,
                        "Card Code": card_code,
                        "Last Updated": last_updated,
                        "URL": card.get_url(),
                    }
                )

        headers = [
            "Batch",
            "Card User",
            "Card UUID",
            "Card Code",
            "Last Updated",
            "URL",
        ]
        dataset = self._create_dataset(data, headers)

        return dataset


class CodeBatchResource(DataSetMixin):

    def export(self, queryset=None, *args, **kwargs):
        queryset = queryset or self.get_queryset()
        data = []

        for batch in queryset:
            inline_queryset = PurchasingCode.objects.filter(batch=batch)
            for code in inline_queryset:
                if code.group:
                    product = code.group
                else:
                    product = code.get_product_display()
                last_updated = code.updated_at.strftime("%Y-%m-%d, %H:%M %p")
                data.append(
                    {
                        "Batch": str(batch),
                        "Code": code.code,
                        "Password": code.password,
                        "Duration": code.duration,
                        "Product": product,
                        "Card": code.card if code.card else "No Card connected yet",
                        "Last Updated": last_updated,
                    }
                )

        headers = [
            "Batch",
            "Code",
            "Password",
            "Duration",
            "Product",
            "Card",
            "Last Updated",
        ]
        dataset = self._create_dataset(data, headers)

        return dataset


@admin.register(URLBatch)
class URLBatchAdmin(ExportWithInlineMixin, admin.ModelAdmin):
    resource_class = URLBatchResource
    list_display = ["__str__", "count", "created_at", "user"]
    readonly_fields = ["user"]
    search_fields = ["count", "user__username"]
    inlines = [NFCCardInline]
    actions = [archive_selected, "export_selected_records"]
    change_list_template = "admin/custom_change_list.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=False)

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-url-batch/', self.admin_site.admin_view(self.add_new_batch), name='add_url_batch'),
            path('view-all-urls/', self.admin_site.admin_view(self.view_all), name='view_all_urls'),
        ]
        return custom_urls + urls

    def add_new_batch(self, request):
        return HttpResponseRedirect(reverse('admin:url_bulk'))

    def view_all(self, request):
        return HttpResponseRedirect(reverse('admin:cards_nfccard_changelist'))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['url_batch'] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(CodeBatch)
class CodeBatchAdmin(ExportWithInlineMixin, admin.ModelAdmin):
    resource_class = CodeBatchResource
    list_display = ["__str__", "count", "created_at", "user"]
    readonly_fields = ["user"]
    search_fields = ["count", "user__username"]
    inlines = [PurchasingCodeInline]
    actions = [archive_selected, "export_selected_records"]
    change_list_template = "admin/custom_change_list.html"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(archive=False)

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-code-batch/', self.admin_site.admin_view(self.add_new_batch), name='add_code_batch'),
            path('view-all-codes/', self.admin_site.admin_view(self.view_all), name='view_all_codes'),
        ]
        return custom_urls + urls

    def add_new_batch(self, request):
        return HttpResponseRedirect(reverse('admin:code_bulk'))

    def view_all(self, request):
        return HttpResponseRedirect(reverse('admin:cards_purchasingcode_changelist'))
