# coding:utf-8

import sys
major, minor, micro, releaselevel, serial = sys.version_info


if major == 2:
    def is_number(v):
        return isinstance(v, (int, long, float))

    def is_unicode_string(v):
        return isinstance(v, unicode)

    def is_non_unicode_string(v):
        return isinstance(v, (str, bytes, bytearray))

    def unicode_str(v):
        return unicode(v)

    from itertools import izip_longest
    zip_longest = izip_longest

    def keypath_value(dic, *keypath):
        return reduce(lambda d, k: d.get(k), [dic] + list(keypath))

elif major == 3:
    def is_number(v):
        return isinstance(v, (int, float))

    def is_unicode_string(v):
        return isinstance(v, str)

    def is_non_unicode_string(v):
        return isinstance(v, (bytes, bytearray))

    def unicode_str(v):
        return str(v)

    from itertools import zip_longest

    from functools import reduce

    def keypath_value(dic, *keypath):
        return reduce(lambda d, k: d.get(k), [dic] + list(keypath))
