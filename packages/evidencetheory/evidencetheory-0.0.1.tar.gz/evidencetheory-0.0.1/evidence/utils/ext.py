#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-03-03 14:27:39
# @Last Modified by:   Jonathan Prieto 
# @Last Modified time: 2015-03-03 16:27:58

from evidence.utils.lib import memo
from itertools import product

__all__ = ['binary']

def binary(l, A):
    """Binary number of l length of A integer value.
    """
    assert l > 0 and 0 <= A <= (1 << l), '(l,A): A is out of range' 
    n = bin(A)[2:]
    return '0' * (l - len(n)) + n


def cardinal(A):
    """Cardinal of subset associated to A as binary number.
    """
    card = 0
    while A > 0:
        card += (A & 1)
        A >>= 1
    return card


bs_ = []


def interXA(n, A, b=0, i=0):
    """Binary numbers with nonempty intersection with A
        of length n.
    """
    global bs_
    if i == n:
        bs_ += [b]
    else:
        if A & (1 << i) == 0:
            interXA(n, A, b, i + 1)
        interXA(n, A, b | (1 << i), i + 1)


@memo
def interXY(n, A=0):
    """A generator to iterate over subsets such that:
       X\cap Y = A \forall X,Y,A \in 2^\Theta |\Theta| = n
    """
    global bs_
    bs_ = []
    interXA(n, A)
    for x, y in product(bs_, bs_):
        if x & y == A:
            yield x, y


def interXY_(n, A):
    for i in range(1 << n):
        for j in range(1 << n):
            if i & j == A:
                yield (i, j)
