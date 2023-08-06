# coding: utf-8
import json
import warnings
from functools import reduce
from config_parser.enums import ConversionTypeEnum
from config_parser.exceptions import ConversionTypeError
from config_parser.conversions import CONVERSION_TABLE

__author__ = 'damirazo <me@damirazo.ru>'


class ConfigParser(object):
    u"""
    Парсер конфигурационных файлов в формате json
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self._fd = open(self.file_path)
        self.data = json.load(self._fd)
        # Таблица соответствия типов конвертирования и конвертирующих функций
        self.conversion_table = CONVERSION_TABLE

    def __del__(self):
        self._fd.close()

    def register_conversion_handler(self, name, handler):
        u"""
        Регистрация обработчика конвертирования

        :param name: Имя обработчика в таблице соответствия
        :param handler: Обработчик
        """
        if name in self.conversion_table:
            warnings.warn((
                u'Конвертирующий тип с именем {} уже '
                u'существует и будет перезаписан!'
            ).format(name))

        self.conversion_table[name] = handler

    def conversion_handler(self, name):
        u"""
        Возвращает обработчик конвертации с указанным именем

        :param name: Имя обработчика
        :return: callable
        """
        try:
            handler = self.conversion_table[name]
        except KeyError:
            raise KeyError((
                u'Конвертирующий тип с именем {} отсутствует '
                u'в таблице соответствия!'
            ).format(name))

        return handler

    def has_param(self, key):
        u"""
        Проверка существования параметра с указанным именем

        :param key: Имя параметра
        """
        return self.get(key) is not None

    def get(self, key, default=None):
        u"""
        Возвращает значение с указанным ключем

        Пример вызова:
        value = self.get('system.database.name')

        :param key: Имя параметра
        :param default: Значение, возвращаемое по умолчанию
        :return: mixed
        """
        segments = key.split('.')
        result = reduce(
            lambda dct, k: dct and dct.get(k) or None,
            segments, self.data)

        return result or default

    def get_converted(self, key, conversion_type, default=None):
        u"""
        Возвращает значение, приведенное к типу,
        соответствующему указанному типу из таблицы соответствия

        :param key: Имя параметра
        :param conversion_type: Имя обработчика конвертации
            из таблицы соответствия
        :param default: Значение по умолчанию
        :return: mixed
        """
        # В случае отсутствия параметра сразу возвращаем значение по умолчанию
        if not self.has_param(key):
            return default

        value = self.get(key, default=default)
        handler = self.conversion_handler(conversion_type)

        try:
            value = handler(value)
        except Exception as exc:
            raise ConversionTypeError((
                u'Произошла ошибка при попытке преобразования типа: {}'
            ).format(exc))

        return value

    def get_by_type(self, key, conversion_func, default=None):
        u"""
        Возвращает значение, приведенное к типу
        с использованием переданной функции

        :param key: Имя параметра
        :param conversion_func: callable объект,
            принимающий и возвращающий значение
        :param default: Значение по умолчанию
        :return: mixed
        """
        if not self.has_param(key):
            return default

        value = self.get(key, default=default)

        try:
            value = conversion_func(value)
        except Exception as exc:
            raise ConversionTypeError((
                u'Произошла ошибка при попытке преобразования типа: {}'
            ).format(exc))

        return value

    # -------------------------------------------------------------------------
    # Синтаксический сахар
    # -------------------------------------------------------------------------

    def get_int(self, key, default=None):
        u"""
        Возвращает значение, приведенное к числовому
        """
        return self.get_converted(
            key, ConversionTypeEnum.INTEGER, default=default)

    def get_bool(self, key, default=None):
        u"""
        Возвращает значение, приведенное к булеву
        """
        return self.get_converted(
            key, ConversionTypeEnum.BOOL, default=default)