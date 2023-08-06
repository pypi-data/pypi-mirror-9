#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-03-03 14:27:35
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2015-03-03 16:28:01

from functools import wraps
from time import time

from evidence.utils import DEBUG

__all__ = ['debug', 'timing', 'memo']

def debug(*args):
    if DEBUG:
        try:
            print ''.join(map(str, args))
        except Exception, e:
            print e


def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print 'func:%r args:[%r, %r] took: %2.4f sec' % \
            (f.__name__, args, kw, te - ts)
        return result
    return wrap


def memo(func):
    cache = {}
    @wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap
