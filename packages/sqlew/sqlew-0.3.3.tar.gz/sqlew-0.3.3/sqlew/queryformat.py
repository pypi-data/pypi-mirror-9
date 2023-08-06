# coding:utf-8

import re
from datetime import datetime, date
from . import compat
from .exceptions import (QueryFormatError,
                         IncompatibleTypeError)

PLACEHOLDER = re.compile(r'([^:]*)(:+)([0-9a-zA-Z_]+)')


def qformat(fmt, **kwargs):
    def _(m):
        pre, head, key = m.groups()

        if pre == '\\':
            return head + key

        else:
            v = kwargs[key]
            should_escape = head == ':'
            return pre + qformat_object(v, should_escape)

    try:
        return PLACEHOLDER.sub(_, fmt)

    except KeyError as e:
        raise QueryFormatError(str(e))


def qformat_object_default(v, escape=True, nested=False):
    if isinstance(v, bool):
        return u'1' if v else u'0'

    if compat.is_number(v):
        return compat.unicode_str(v)

    if compat.is_non_unicode_string(v):
        return qformat_object(v.decode('utf8'), escape, nested)

    if compat.is_unicode_string(v):
        return u"'{}'".format(v.replace(u"'", u"\\'")) if escape else v

    if v is None:
        return u'NULL'

    if isinstance(v, (list, tuple, set)):
        s = u','.join([qformat_object(e, escape, True) for e in v])
        return u'({})'.format(s) if nested else s

    if isinstance(v, dict):
        d = {qformat_object(k, False, True): qformat_object(e, True, True)
             for k, e in v.items()}
        return u','.join([u'{}={}'.format(k, e) for k, e in d.items()])

    if hasattr(v, '__call__'):
        r = v()
        fname, args = (r[0], r[1:]) if isinstance(r, tuple) else (r, ())
        return u'{}({})'.format(fname.upper(), qformat_object(args))

    if isinstance(v, datetime):
        return u"'{}'".format(v.strftime('%Y-%m-%d %H:%M:%S'))

    if isinstance(v, date):
        dt = datetime(v.year, v.month, v.day)
        return "'{}'".format(dt.strftime('%Y-%m-%d'))

    raise IncompatibleTypeError(v, escape, nested)


qformat_object = qformat_object_default
