from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth import get_user_model

User = get_user_model()

PRODUCTS_CHOICES = [
    ("product1", "Product 1"),
    ("product2", "Product 2"),
    ("product3", "Product 3"),
    ("product4", "Product 4"),
]


class ProductGroup(models.Model):
    title = models.CharField("Title", max_length=500)
    products = models.CharField(
        "Products", max_length=500
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Product Groups"
        ordering = ("-created_at",)

    def get_products_display(self):
        if self.products:
            return ', '.join([dict(PRODUCTS_CHOICES).get(item, item) for item in self.products.split(',')])
        return ''

    def __str__(self):
        return self.title


class LinkDuration(models.Model):
    duration = models.PositiveIntegerField("Duration in Years", default=1)

    class Meta:
        verbose_name = "Link Duration"
        verbose_name_plural = "Link Durations"
        ordering = ("-id",)

    def __str__(self):
        return f"Link duration: {self.duration}"


class CRUDLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    object_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField("Created At", auto_now_add=True)

    def __str__(self):
        return f"{self.action} ({self.object_name}) by {self.user} at {self.timestamp.strftime('%Y-%m-%d, %H:%M %p')}"

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        ordering = ("-timestamp",)
