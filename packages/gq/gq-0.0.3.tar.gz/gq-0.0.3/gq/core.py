# -*- coding: utf-8 -*-

import re
import json
import os
from operator import itemgetter

from missing import ValMissing
from expr import Node, Expression
from pbar import ProgressBar

def gq(rootdir, params):
    return Selector(rootdir, params)

def mtable_to_dict(maf_id_file):
    """ maf_id_tableからdictへの変換
    """

    out = []

    pattern = re.compile(r'(?P<id>\d+)\t\{(?P<json>.+)\}')
    for line in maf_id_file:
        m = pattern.match(line)
        text = '{"id": ' + m.group('id') + ', ' + m.group('json').replace("'", '"') + '}'
        out.append( json.loads(text) )

    return out

def setup_maf(rootdir):
    with open(os.path.join(rootdir, '.maf_id_table.tsv'), 'r') as f:
        p = mtable_to_dict(f)
    return Selector(rootdir, p)

id_pattern = re.compile(r'(?P<id>\d+?)-.+')

def get_id(fname):
    m = id_pattern.match(fname)
    if m:
        return int(m.group('id'))

class Selector(ValMissing):
    def __init__(self, rootdir, params, curdir=None, filter=None, next_is_or=False, onGet=lambda f: f):
        self.rootdir = os.path.abspath(os.path.expanduser(rootdir))
        self.params = params
        if curdir:
            self.curdir = curdir
        else:
            self.curdir = self.rootdir
        self.filter = filter
        self.next_is_or = next_is_or
        self.onGet = onGet

    def val_missing(self, name):
        if name.startswith('_'):
            return Node(name[1:])
        else:
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__, name))

    def __call__(self, d):
        return Selector(self.rootdir, self.params,
                        curdir=os.path.join(self.curdir, d),
                        filter=self.filter,
                        onGet=self.onGet)

    def where(self, expr):
        if not isinstance(expr, Expression):
            raise TypeError("Expression is required")

        if self.filter:
            keys = self.filter.get_node_names()
        else:
            keys = []
        keys.extend(expr.get_node_names())

        params = self._filter_params_with_keys(keys)

        if self.filter:
            if self.next_is_or:
                return Selector(self.rootdir, params,
                                curdir=self.curdir,
                                filter=self.filter | expr,
                                onGet=self.onGet)
            else:
                return Selector(self.rootdir, params,
                                curdir=self.curdir,
                                filter=self.filter & expr,
                                onGet=self.onGet)
        else:
            return Selector(self.rootdir, params,
                            curdir=self.curdir,
                            filter=expr,
                            onGet=self.onGet)

    def or_(self):
        return Selector(self.rootdir, self.params,
                        curdir=self.curdir,
                        filter=self.filter,
                        next_is_or=True,
                        onGet=self.onGet)

    def sortby(self, *keys):
        keys = [k.name for k in keys]
        params = sorted(self._filter_params_with_keys(keys), key=itemgetter(*keys))
        return Selector(self.rootdir, params,
                        curdir=self.curdir,
                        filter=self.filter,
                        onGet=self.onGet)

    def _filter_params_with_keys(self, keys):
        params = self.params
        for k in keys:
            params = filter(lambda p: p.has_key(k), params)
        return params

    def _valid_params(self):
        ids = [get_id(fname) for fname in os.listdir( self.curdir )]
        if self.filter:
            valids = filter(lambda p: (p['id'] in ids) and (self.filter.eval(p)), self.params)
        else:
            valids = filter(lambda p: p['id'] in ids, self.params)
        return valids

    def size(self):
        v = self._valid_params()
        return len(v)

    def get(self, onGet=None):
        out = []
        # for p in self.params:
        #     fname = os.path.join(self.curdir, ('%d-' % p['id']) + os.path.split(self.curdir)[1])
        #     print fname
        #     if os.path.exists(fname) and self.filter.eval(p):
        #         if onGet:
        #             out.append( onGet(open(fname)) )
        #         else:
        #             out.append( self.onGet(open(fname)) )

        valids = self._valid_params()
        pbar = ProgressBar(num_iter=len(valids))

        if not onGet:
            onGet = self.onGet
        for i, v in enumerate(valids):
            fname = os.path.join(self.curdir, ('%d-' % v['id']) + os.path.split(self.curdir)[1])
            out.append( onGet(open(fname)) )
            pbar.update(i)

        return out
