# coding:utf-8

import os


class Storage(dict):
    def load(self, path):
        for f in self._load(path):
            with open(f, 'r') as fp:
                key = f[len(path):].lstrip('/')[:-4]
                self[key] = self._make_compact(fp.read())

    def _load(self, path):
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith('.sql'):
                    yield os.path.join(root, f)

    def _make_compact(self, q):
        all_lines = q.splitlines()
        query_lines = [l for l in all_lines if not l.startswith(('#', '--'))]
        query = ' '.join(query_lines)
        return ' '.join(query.split())
