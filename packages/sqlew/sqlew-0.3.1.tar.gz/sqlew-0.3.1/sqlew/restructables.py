# coding:utf-8


class RestructableDict(dict):
    def nest_dict(self, name, keymap):
        d = {keymap[k]: self.pop(k) for k in keymap.keys()}
        self[name] = RestructableDict(d)
        return self

    def nest_list(self, name, keymap, separator=','):
        d = {keymap[k]: self.pop(k) for k in keymap.keys()}

        ret = []
        for k, v in d.items():
            if v is not None:
                for i, e in enumerate(v.split(separator)):
                    if i < len(ret):
                        ret[i][k] = e
                    else:
                        ret.append({k: e})

        self[name] = RestructableList(ret)
        return self

    def nest(self, name, separator=None):
        keymap = {k: k[len(name)+1:]
                  for k in self.keys() if k.startswith(name + '_')}

        if separator is None:
            return self.nest_dict(name, keymap)

        else:
            return self.nest_list(name, keymap, separator)


class RestructableList(list):
    def nest_dict(self, name, keymap):
        for e in self:
            e.nest_dict(name, keymap)
        return self

    def nest_list(self, name, keymap, separator=','):
        for e in self:
            e.nest_list(name, keymap, separator)
        return self

    def nest(self, name, separator=None):
        for e in self:
            e.nest(name, separator)
        return self
