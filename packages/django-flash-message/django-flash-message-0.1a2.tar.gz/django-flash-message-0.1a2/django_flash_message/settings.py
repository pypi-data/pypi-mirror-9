# -*- coding:utf-8 -*-
# PROJECT_NAME : django-flash-message
# FILE_NAME    : 
# AUTHOR       : younger shen

# you could set the storage to session or cookie , if you set to session , the message will store in session,
# file or db or anything else, if you set to cookie , the message will store in cookie
DJANGO_FLASH_MESSAGE_STORAGE = 'session'

# the name of cookie used, you set this variable only if you set the storage to cookie
DJANGO_FLASH_MESSAGE_COOKIE_NAME = 'flash_message'

