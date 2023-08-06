# coding: utf-8

__author__ = 'damirazo <me@damirazo.ru>'


class ConversionTypeEnum(object):
    u"""
    Перечисления доступных типов для конвертации
    при парсинге шаблона конфигурации
    """

    STRING = 'string'
    INTEGER = 'integer'
    DECIMAL = 'decimal'
    BOOL = 'bool'