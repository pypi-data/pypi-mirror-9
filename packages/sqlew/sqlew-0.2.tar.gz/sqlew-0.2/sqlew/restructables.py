# coding:utf-8


class RestructableDict(dict):
    def split(self, key, separator=','):
        if self[key] is not None:
            self[key] = self[key].split(separator)

        else:
            self[key] = []

        return self

    def form_one(self, from_key, to_key):
        from_keypath = from_key.split('.')
        to_keypath = to_key.split('.')

        dst_head = self
        for k in to_keypath[:-1]:
            dst_head = dst_head.setdefault(k, RestructableDict())

        src_head = self
        for k in from_keypath[:-1]:
            src_head = src_head[k]

        dst_head[to_keypath[-1]] = src_head[from_keypath[-1]]
        del src_head[from_keypath[-1]]

        return self

    def form(self, from_prefix, to_prefix):
        for k in self.keys():
            if k.startswith(from_prefix):
                suffix = k[len(from_prefix):]
                to_key = '{}.{}'.format(to_prefix, suffix)
                self.form_one(k, to_key)

        return self

    def transpose(self, key, separator=','):
        ret = RestructableList()
        for k, joined in self[key].items():
            if joined is not None:
                splited = joined.split(separator)
                for i, v in enumerate(splited):
                    if len(ret) < i+1:
                        ret.append(RestructableDict())

                    ret[i][k] = v
        self[key] = ret

        return self


class RestructableList(list):
    def split(self, key, separator=','):
        for e in self:
            e.split(key, separator)

        return self

    def form_one(self, from_key, to_key):
        for e in self:
            e.form_one(from_key, to_key)

        return self

    def form(self, from_prefix, to_prefix):
        for e in self:
            e.form(from_prefix, to_prefix)

        return self

    def transform(self, key, separator=','):
        for e in self:
            e.transpose(key, separator)

        return self
