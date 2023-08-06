# coding=utf-8

from django.conf import settings


LOGIN = getattr(settings, 'SMSC_LOGIN', '')
PASSWORD = getattr(settings, 'SMSC_PASSWORD', '')
SENDER = getattr(settings, 'SMSC_SENDER', '')

SEND_URL = getattr(settings, 'SMSC_SEND_URL', 'https://smsc.ru/sys/send.php')
STATUS_URL = getattr(settings, 'SMSC_STATUS_URL', 'https://smsc.ru/sys/status.php')
