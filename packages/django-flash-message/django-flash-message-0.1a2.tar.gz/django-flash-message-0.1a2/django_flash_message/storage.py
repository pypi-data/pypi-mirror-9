# -*- coding:utf-8 -*-
# PROJECT_NAME : django-flash-message
# FILE_NAME    : 
# AUTHOR       : younger shen
from .utils import generate_settings
from .patch import cookie_add_message
from .patch import cookie_get_message
from .patch import session_add_message
from .patch import session_get_message

settings = generate_settings()


class BaseStorage(type):

    def __init__(cls, name, bases, dct):
        storage_type = settings.get('STORAGE')
        if storage_type == 'cookie':
            setattr(cls, 'get_message', cookie_get_message)
            setattr(cls, 'add_message', cookie_add_message)
        else:
            setattr(cls, 'get_message', session_get_message)
            setattr(cls, 'add_message', session_add_message)

        super(BaseStorage, cls).__init__(name, bases, dct)

    def __new__(mcs, name, bases, dct):
        return type.__new__(mcs, name, bases, dct)


class Storage(object):
    __metaclass__ = BaseStorage

    @classmethod
    def add_message(cls, request, key, value):
        pass

    @classmethod
    def get_message(cls, request, key):
        pass

storage = Storage()