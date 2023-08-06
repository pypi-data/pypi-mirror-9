# -*- coding:utf-8 -*-
# PROJECT_NAME : django-flash-message
# FILE_NAME    : 
# AUTHOR       : younger shen
from .utils import generate_settings
from .exceptions import MessageSafeException
settings = generate_settings()


def session_add_message(cls, request, key, value, safe=True):

    if safe:
        if request.session.get(key):
            raise MessageSafeException
    request.session[key] = value


def cookie_add_message(cls, request, response, key, value, safe=True):
    if safe:
        if key in request.COOKIES:
            raise MessageSafeException()
    response.set_cookie(key, value=value)


def session_get_message(cls, request, key, default=None):
    value = None
    if request.session.get(key):
        value = request.session.get(key)
        del request.session[key]

    return value if value else default


def cookie_get_message(cls, request, response, key, default=None):
    value = None

    if request.COOKIES.get(key):
        value = request.COOKIES.get(key)
        response.delete_cookie(key)

    return value if value else default