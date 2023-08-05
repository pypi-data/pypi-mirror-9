# coding=utf-8

from datetime import timedelta

from django.core.management.base import NoArgsCommand
from django.utils import timezone

from smsaero import models as _models
from smsaero import api as _api


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        full_day = timezone.now() - timedelta(days=1)
        # выбираем сообщения не старше суток
        messages = _models.Message.objects.filter(created__gt=full_day)
        for message in messages:
            status = _api.get_status(message.identifier)
            message.status = status
            message.save(update_fields=['status'])
        print u'{0} messages have been updated'.format(messages.count())
