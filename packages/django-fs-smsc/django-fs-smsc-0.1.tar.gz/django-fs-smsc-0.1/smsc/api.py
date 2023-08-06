# coding=utf-8

import requests
from hashlib import md5

from smsc import settings as _settings
from smsc import models as _models
from smsc import exceptions as _exceptions


def smsc_request(url, params):
    data = {
        'login': _settings.LOGIN,
        'psw': md5(_settings.PASSWORD).hexdigest(),
        'charset': 'utf-8',
        'fmt': 3,
    }
    data.update(params)
    response = requests.get(url, params=data)
    answer = response.json()
    return answer


def send_sms(phone, text):
    message = _models.Message.objects.create(phone=phone, text=text)
    params = {
        'id': message.id,
        'phones': message.phone,
        'mes': message.text,
        'sender': _settings.SENDER,
    }
    answer = smsc_request(_settings.SEND_URL, params)
    if 'error' in answer:
        raise _exceptions.SMSCException(answer)
