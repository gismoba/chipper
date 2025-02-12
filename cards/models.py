from core.utils import unique_code_generator, unique_password_generator
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from hitcount.models import HitCount
from settings.models import PRODUCTS_CHOICES, LinkDuration, ProductGroup

User = get_user_model()


class URLBatch(models.Model):
    count = models.PositiveBigIntegerField("Quantity", blank=True, null=True)
    archive = models.BooleanField("Archive?", default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    user = models.ForeignKey(
        User,
        related_name="user_created_url_batches",
        verbose_name="User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "URL Batch"
        verbose_name_plural = "URL Batches"
        ordering = ("-created_at",)

    def __str__(self):
        # return f"{self.count} URLs Generated at {self.created_at.strftime('%Y-%m-%d, %H:%M %p')} By {self.user}"
        return f"Batch {self.created_at.strftime('%Y-%m-%d, %H:%M %p')} By {self.user}"


class CodeBatch(models.Model):
    count = models.PositiveBigIntegerField("Quantity", blank=True, null=True)
    archive = models.BooleanField("Archive?", default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    user = models.ForeignKey(
        User,
        related_name="user_created_code_batches",
        verbose_name="User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Code Batch"
        verbose_name_plural = "Code Batches"
        ordering = ("-created_at",)

    def __str__(self):
        # return f"{self.count} Purchasing Codes Generated at {self.created_at.strftime('%Y-%m-%d, %H:%M %p')} By {self.user}"
        return f"Batch {self.created_at.strftime('%Y-%m-%d, %H:%M %p')} By {self.user}"


class NFCCard(models.Model):
    user = models.ForeignKey(
        User,
        related_name="user_cards",
        verbose_name="User",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    uuid = models.UUIDField(default="", editable=False, unique=True)
    batch = models.ForeignKey(
        URLBatch,
        related_name="batch_urls",
        verbose_name="Batch",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    password = models.CharField("Password", blank=True, null=True, max_length=50)
    title = models.CharField("Title", blank=True, null=True, max_length=50)
    data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "URL"
        verbose_name_plural = "URLs"
        ordering = ("-created_at",)

    def get_url(self):
        base_url = "http://127.0.0.1:8000/services/landingPage/"
        return f"{base_url}{self.uuid}/"

    def check_password(self, password):
        return self.password == password

    hit_count_generic = GenericRelation(
        HitCount, object_id_field='object_pk',
        related_query_name='hit_count_generic_relation'
    )

    def __str__(self):
        if self.title:
            return self.title
        return str(self.uuid)

    def get_absolute_url(self):
        return reverse("cards:landing_page", args=[self.uuid])


class PurchasingCode(models.Model):
    code = models.CharField(
        "Purchasing Code",
        blank=True,
        null=True,
        unique=True,
        max_length=120,
        help_text="automatically generated",
    )
    password = models.CharField(
        "Password",
        blank=True,
        null=True,
        max_length=120,
        help_text="automatically generated",
    )
    batch = models.ForeignKey(
        CodeBatch,
        related_name="batch_codes",
        verbose_name="Batch",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    group = models.ForeignKey(
        ProductGroup,
        related_name="group_codes",
        verbose_name="Group",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    product = models.CharField(
        "Product", blank=True, null=True, max_length=500, choices=PRODUCTS_CHOICES
    )
    card = models.OneToOneField(
        NFCCard,
        related_name="card_code",
        verbose_name="Card",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    duration = models.ForeignKey(
        LinkDuration,
        verbose_name="Duration",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Purchasing Code"
        verbose_name_plural = "Purchasing Codes"
        ordering = ("-created_at",)

    def __str__(self):
        return self.code

    def generate_code(self):
        if not self.code:
            self.code = unique_code_generator(self)

