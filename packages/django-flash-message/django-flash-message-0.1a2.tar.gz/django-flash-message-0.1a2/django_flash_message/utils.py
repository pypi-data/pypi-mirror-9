# -*- coding:utf-8 -*-
# PROJECT_NAME : django-flash-message
# FILE_NAME    : 
# AUTHOR       : younger shen
from django.conf import settings
from .settings import DJANGO_FLASH_MESSAGE_COOKIE_NAME
from .settings import DJANGO_FLASH_MESSAGE_STORAGE


def generate_settings():
    ret = dict()
    ret['STORAGE'] = getattr(settings, 'DJANGO_FLASH_MESSAGE_STORAGE', DJANGO_FLASH_MESSAGE_STORAGE)

    if ret['STORAGE'] == 'cookie':
        ret['COOKIE_NAME'] = getattr(settings, 'DJANGO_FLASH_MESSAGE_COOKIE_NAME', DJANGO_FLASH_MESSAGE_COOKIE_NAME)

    return ret