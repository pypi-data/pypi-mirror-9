# coding=utf-8

import requests
from hashlib import md5

from smsaero import settings as _settings
from smsaero import exceptions as _exceptions
from smsaero import models as _models


def smsaero_post(url, params):
    data = {
        'answer': 'json',
        'user': _settings.USER,
        'password': md5(_settings.PASSWORD).hexdigest(),
        'from': _settings.SIGNATURE,
    }
    data.update(params)
    response = requests.post(url, data=data)
    answer = response.json()
    return answer


def send_sms(phone, text):
    params = {
        'to': phone,
        'text': text,
    }
    answer = smsaero_post(_settings.SEND_URL, params)
    if answer['result'] != 'accepted':
        raise _exceptions.SMSAeroException(answer)
    _models.Message.objects.create(phone=phone, text=text, identifier=answer['id'])


def get_status(identifier):
    params = {
        'id': identifier,
    }
    answer = smsaero_post(_settings.STATUS_URL, params)
    if answer['result'] == 'reject':
        return answer['reason']
    return answer['result']
