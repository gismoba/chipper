import uuid

from core.utils import unique_code_generator
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver

from .models import PurchasingCode, NFCCard, URLBatch


@receiver(pre_save, sender=PurchasingCode)
def pre_save_code(sender, instance, *args, **kwargs):
    if not instance.code:
        instance.code = unique_code_generator(instance)


@receiver(pre_save, sender=NFCCard)
def pre_save_uuid(sender, instance, *args, **kwargs):
    if not instance.uuid:
        instance.uuid = uuid.uuid4()


@receiver(post_save, sender=URLBatch)
def pre_save_url(sender, instance, **kwargs):
    base_url = "http://127.0.0.1:8000/services/landingPage/"
    cards = instance.batch_urls.all()
    for card in cards:
        url = f"{ base_url }{card.uuid}/"
        card.url = url
        card.save()
