# coding: utf-8
from config_parser.parser import ConfigParser

__author__ = 'damirazo <me@damirazo.ru>'


if __name__ == '__main__':
    parser = ConfigParser('config.json')

    print(parser.get('foo'))
    print(parser.get('foo.bar'))
    print(parser.get_bool('foo.boolean_value'))