# -*- coding: utf-8 -*-

from missing import ValMissing
from expr import Node, Expression
from pbar import ProgressBar

import re
import json
import os

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

id_pattern = re.compile(r'(?P<id>\d+?)-.+')

def get_id(fname):
    m = id_pattern.match(fname)
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
        elif self.filter:
            if self.next_is_or:
                return Selector(self.rootdir, self.params,
                                curdir=self.curdir,
                                filter=self.filter | expr,
                                onGet=self.onGet)
            else:
                return Selector(self.rootdir, self.params,
                                curdir=self.curdir,
                                filter=self.filter & expr,
                                onGet=self.onGet)
        else:
            return Selector(self.rootdir, self.params,
                            curdir=self.curdir,
                            filter=expr,
                            onGet=self.onGet)

    def or_(self):
        return Selector(self.rootdir, self.params,
                        curdir=self.curdir,
                        filter=self.filter,
                        next_is_or=True,
                        onGet=self.onGet)

    def _valid_params(self):
        ids = [get_id(fname) for fname in os.listdir( self.curdir )]
        valids = filter(lambda p: (p['id'] in ids) and (self.filter.eval(p)), self.params)
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
