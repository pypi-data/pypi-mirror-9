# -*- coding:utf-8 -*-
# PROJECT_NAME : django-flash-message
# FILE_NAME    : 
# AUTHOR       : younger shen


class MessageSafeException(Exception):

    def __init__(self, message=None):
        self.message = message if message else u'key exists in session or cookie, if you still wanna save the value , set safe=False'

    def __str__(self):
        return self.message