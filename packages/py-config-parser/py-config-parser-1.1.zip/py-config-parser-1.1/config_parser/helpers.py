# coding: utf-8
__author__ = 'damirazo <me@damirazo.ru>'


def boolean_conversion_handler(value):
    u"""
    Приведение значения к булеву
    """
    value = value.lower()
    if value in ('true', 'false'):
        return value == 'true'

    return bool(value)