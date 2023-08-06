# coding:utf-8

import re
from datetime import datetime
from .exceptions import QueryFormatError

PLACEHOLDER = re.compile(r'.:+[0-9a-zA-Z_]+')


def qformat(fmt, **kwargs):
    def _(m):
        g = m.group(0)
        pre, key = g[0], g[1:]

        if pre == '\\':
            return key

        else:
            v = kwargs[key.lstrip(':')]
            v = str(v) if key.startswith('::') else escape(v)
            return pre + v

    try:
        return PLACEHOLDER.sub(_, fmt)

    except KeyError as e:
        raise QueryFormatError(str(e))


def escape(v):
    if isinstance(v, (int, long, float)):
        return str(v)

    elif isinstance(v, bool):
        return '1' if v else '0'

    elif isinstance(v, (str, unicode)):
        return "'{}'".format(str(v).replace("'", "\\'"))

    elif v is None:
        return 'NULL'

    elif isinstance(v, (list, tuple, set)):
        return ','.join([value(e) for e in v])

    elif isinstance(v, datetime):
        return "'{}'".format(v.strftime('%Y-%m-%d %H:%M:%S'))

    raise TypeError('Incompatible type :{}'.format(v))
