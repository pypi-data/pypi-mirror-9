# coding:utf-8

from . import compat


class RestructableDict(dict):
    def nest(self, *keypath):
        head, tail = keypath[0], keypath[1:]

        if len(keypath) == 1:
            keys = list(self.keys())
            d = {k[len(head)+1:]: self.pop(k) for k in keys
                 if k.startswith(head + '_')}
            self[head] = RestructableDict(d)

        else:
            self[head].nest(*tail)

        return self

    def split(self, *keypath):
        head, tail = keypath[0], keypath[1:]

        if len(keypath) == 1:
            v = self[head].split(',') if self[head] is not None else []
            self[head] = RestructableList(v)

        else:
            self[head].split(*tail)

        return self

    def invert(self, *keypath):
        head, tail = keypath[0], keypath[1:]

        if len(keypath) == 1:
            keys = self[head].keys()
            ls = [RestructableDict(dict(zip(keys, e)))
                  for e in compat.zip_longest(*self[head].values())]
            self[head] = RestructableList(ls)

        else:
            self[head].invert(*tail)

        return self

    def nest_list(self, *keypath):
        self.nest(*keypath)
        rst = compat.keypath_value(self, *keypath)
        for k in rst.keys():
            rst.split(k)
        return self.invert(*keypath)


class RestructableList(list):
    def nest(self, *keypath):
        for e in self:
            e.nest(*keypath)
        return self

    def split(self, *keypath):
        for e in self:
            e.split(*keypath)
        return self

    def invert(self, *keypath):
        for e in self:
            e.invert(*keypath)
        return self

    def nest_list(self, *keypath):
        for e in self:
            e.nest_list(*keypath)
        return self
