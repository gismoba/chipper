from django.db import models
from cards.models import URLBatch, CodeBatch


class URLBatchArchived(URLBatch):
    class Meta:
        proxy = True
        verbose_name = 'URL Archive'
        verbose_name_plural = 'URL Archive'


class CodeBatchArchived(CodeBatch):
    class Meta:
        proxy = True
        verbose_name = 'Code Archive'
        verbose_name_plural = 'Code Archive'
