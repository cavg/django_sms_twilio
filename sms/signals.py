from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from sms.models import Quota

import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_default_quote_limit(sender, instance, created, **kwargs):
    if created:
        if not Quota.objects.filter(user=instance).exists():
            Quota.objects.create(
                user = instance
            )