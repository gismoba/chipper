from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from cards.models import URLBatch, CodeBatch, NFCCard, PurchasingCode
from archive.models import URLBatchArchived, CodeBatchArchived
from .models import CRUDLog, LinkDuration, ProductGroup
from .middleware import get_current_user

User = get_user_model()


@receiver(post_save, sender=URLBatch)
@receiver(post_save, sender=CodeBatch)
@receiver(post_save, sender=NFCCard)
@receiver(post_save, sender=PurchasingCode)
@receiver(post_save, sender=ProductGroup)
@receiver(post_save, sender=URLBatchArchived)
@receiver(post_save, sender=CodeBatchArchived)
@receiver(post_save, sender=LinkDuration)
def log_object_creation_update(sender, instance, created, **kwargs):
    if created:
        action = 'CREATE'
    else:
        action = 'UPDATE'
    
    object_name = str(instance)
    user = get_current_user()

    log_entry = CRUDLog(action=action, object_name=object_name, user=user)
    log_entry.save()


@receiver(post_save, sender=User)
def log_user_creation_update(sender, instance, created, **kwargs):
    if created:
        action = 'CREATE'
    else:
        if instance.is_last_login_updated:
            return
        action = 'UPDATE'
    
    object_name = str(instance)
    user = get_current_user()

    log_entry = CRUDLog(action=action, object_name=object_name, user=user)
    log_entry.save()


@receiver(post_delete, sender=URLBatch)
@receiver(post_delete, sender=CodeBatch)
@receiver(post_delete, sender=ProductGroup)
@receiver(post_delete, sender=URLBatchArchived)
@receiver(post_delete, sender=CodeBatchArchived)
@receiver(post_delete, sender=LinkDuration)
@receiver(post_delete, sender=User)
def log_object_deletion(sender, instance, **kwargs):
    action = 'DELETE'
    
    object_name = str(instance)
    user = get_current_user()

    log_entry = CRUDLog(action=action, object_name=object_name, user=user)
    log_entry.save()
