# -*- coding: utf-8 -*-
"""
    emmett.serializers
    ------------------

    :copyright: 2014 Giovanni Barillari
    :license: BSD-3-Clause
"""

from functools import partial
from orjson import dumps as _json_dumps, OPT_NAIVE_UTC, OPT_NON_STR_KEYS

from .html import tag, htmlescape

_json_safe_table = {
    'u2028': [r'\u2028', '\\u2028'],
    'u2029': [r'\u2029', '\\u2029']
}


class Serializers:
    _registry_ = {}

    @classmethod
    def register_for(cls, target):
        def wrap(f):
            cls._registry_[target] = f
            return f
        return wrap

    @classmethod
    def get_for(cls, target):
        return cls._registry_[target]


def _json_default(obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    raise TypeError


json = partial(
    _json_dumps,
    default=_json_default,
    option=OPT_NON_STR_KEYS | OPT_NAIVE_UTC
)


def json_safe(value):
    rv = json(value)
    for val, rep in _json_safe_table.values():
        rv.replace(val, rep)
    return rv


def xml_encode(value, key=None, quote=True):
    if hasattr(value, '__xml__'):
        return value.__xml__(key, quote)
    if isinstance(value, dict):
        return tag[key](
            *[
                tag[k](xml_encode(v, None, quote))
                for k, v in value.items()
            ])
    if isinstance(value, list):
        return tag[key](
            *[
                tag[item](xml_encode(item, None, quote))
                for item in value
            ])
    return htmlescape(value)


Serializers.register_for('json')(json)


@Serializers.register_for('xml')
def xml(value, encoding='UTF-8', key='document', quote=True):
    rv = ('<?xml version="1.0" encoding="%s"?>' % encoding) + \
        str(xml_encode(value, key, quote))
    return rv
