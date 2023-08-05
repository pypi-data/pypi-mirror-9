# coding=utf-8

from django.conf import settings


SEND_URL = getattr(settings, 'SMSAERO_SEND_URL', 'https://gate.smsaero.ru/send/')
STATUS_URL = getattr(settings, 'SMSAERO_STATUS_URL', 'https://gate.smsaero.ru/status/')

USER = getattr(settings, 'SMSAERO_USER', '')
PASSWORD = getattr(settings, 'SMSAERO_PASSWORD', '')
SIGNATURE = getattr(settings, 'SMSAERO_SIGNATURE', '')
