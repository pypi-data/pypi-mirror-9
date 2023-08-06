# -*- coding: utf-8 -*-

import sys
import math

L = 36

class ProgressBar(object):
    def __init__(self, num_iter):
        self.unit = num_iter * 1.0 / L
        self.iter = num_iter
        sys.stderr.write('\r' + self._bar(0) + '\t' + self._percent(0))

    def update(self, val):
        if val >= self.iter-1:
            sys.stderr.write('\r' + self._bar(val) + '\t' + self._percent(val) + '\n')
        else:
            sys.stderr.write('\r' + self._bar(val) + '\t' + self._percent(val))

    def _bar(self, val):
        progress = int( (val+1) / self.unit )
        return '[' + '#' * progress + ' ' * (L-progress) + ']'

    def _percent(self, val):
        return '%.1f' % ( (val+1) * 100.0 / self.iter ) + '%'

if __name__ == '__main__':
    import time
    p = ProgressBar(num_iter=10)
    for i in range(10):
        time.sleep(1)
        p.update(i)

    print 'finish!'
