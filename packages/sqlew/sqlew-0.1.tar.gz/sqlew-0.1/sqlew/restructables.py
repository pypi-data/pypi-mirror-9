# coding:utf-8


def _mklist(key, separator):
    def _(e):
        e[key] = e[key].split(separator)
    return _


def _mkdict(**rules):
    def _(e):
        for fromkey, tokey in rules.items():
            keypath = tokey.split('.')
            head = e
            for k in keypath[:-1]:
                head = head.setdefault(k, {})
            head[keypath[-1]] = e[fromkey]
            del e[fromkey]
    return _


class RestructableList(list):
    def process(self, f):
        for e in self:
            f(e)
        return self

    def mklist(self, key, separator=','):
        return self.process(_mklist(key, separator))

    def mkdict(self, **rules):
        return self.process(_mkdict(**rules))


class RestructableDict(dict):
    def process(self, f):
        f(self)
        return self

    def mklist(self, key, separator=','):
        return self.process(_mklist(key, separator))

    def mkdict(self, **rules):
        return self.process(_mkdict(**rules))
