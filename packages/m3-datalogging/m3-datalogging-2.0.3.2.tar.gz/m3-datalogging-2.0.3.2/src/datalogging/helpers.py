# coding: utf-8
from django.conf import settings

from m3_legacy.middleware import get_thread_data

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


def get_snapshot(instance):
    u""" Получение снимка состояния экземпляра модели """
    state = set()
    for attr_name, val in instance.__dict__.iteritems():
        if not (attr_name.startswith('_') or
                attr_name in settings.DATALOGGER_EXCLUDE_FIELDS):
            try:
                state.add((attr_name, val))
            except TypeError:
                state.add((attr_name, str(val)))
    return state


def is_server_mode():
    u""" Определение режима работы сервера.
    """
    _thread_locals = get_thread_data()
    return hasattr(_thread_locals, 'request_token')


def only_server_mode(func):
    u""" Предотвращение запуска логгера в шеле
    """
    def wrapper(*a, **kw):
        if is_server_mode():
            return func(*a, **kw)
        else:
            return None
    return wrapper


def memorize_user(user):
    u""" Запоминание пользователя в текущем треде.
    """
    _thread_locals = get_thread_data()
    _thread_locals.suspicious_user = user


def remember_user():
    u""" Вспоминаем пользователя
    """
    _thread_locals = get_thread_data()
    return getattr(_thread_locals, 'suspicious_user', None)
