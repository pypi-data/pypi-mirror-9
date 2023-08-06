#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-02-16 02:22:55
# @Last Modified 2015-02-16
# @Last Modified by:   Jonathan Prieto 
# Classical Dempster-Shafer Theory (DST)

from evidence.utils.lib import debug, memo
from evidence.utils.ext import binary, cardinal, interXY
from math import log

def m(Bel=None, A=None):
    '''
        (bba or m): Basic Belief Assignment
        m(.): 2^\Theta \Rightarrow [0,1]
        m(\emptyset) = 0
        m(A) = \sum_{B\subset A} (-1)^{|A-B|} Bel(B)
        \sum_{A\in 2^\Theta} m(A) = 1
    '''
    if isinstance(Bel, list):
        l = len(Bel)
        if isinstance(A, int):
            if A == 0:
                return 0.00
            assert 0 <= A <= l, 'A should be a valid index for a subset'
            mB = 0
            for idx, B in enumerate(Bel):
                if (idx & ~A) == 0:
                    card = cardinal(A - idx)
                    mB += (-1 if card & 1 else 1) * B
            return mB
        elif not A:
            return lambda x: m(Bel=Bel, A=x)
    return None


def Bel(m=None, A=None):
    '''
        (Bel): Belief (credibility)
        Bel(A) = \sum_{B\in 2^\Theta\, B\subset A} m(A)
    '''
    if isinstance(m, list):
        l = len(m)
        L2 = int(log(l, 2))
        assert l & (l - 1) == 0, 'm should have a lenght 2^\Theta'
        # assert 1. * sum(m) == 1., 'm should be a basic belief assignment'
        if isinstance(A, int):
            debug(binary(L2, A))
            assert 0 <= A <= l, 'A is not a index of a subset'
            bel = 0.
            for idx, B in enumerate(m):
                if idx & ~A == 0:
                    bel += B * 1.
                    debug('\t', binary(L2, idx))
            return bel
        elif not A:
            return lambda x: Bel(m=m, A=x)
    return None


@memo
def sumXYcapA(n, m1, m2, A):
    '''
        \sum_{X,Y\in 2^{\Theta}, X\cap Y=A} m_{1}(X) m_{2}(Y)
    '''
    return sum(m1(X) * m2(Y) for X, Y in interXY(n, A))


def k_12(n, m1, m2):
    '''
        k_{12} = \sum_{X,Y\in 2^{\Theta}, X\cap Y=\emptyset} m_{1}(X) m_{2}(Y)
    '''
    return sumXYcapA(n, m1, m2, 0)


def dempster_rule(n, m1, m2, A=0):
    '''
        Dempster rule of combination m1, m2 as bba
        m(.) = [m_1 + m_2](.)
        The following is the definition:
        m(\emptyset)  = 0
        m(A) =   \sum_{X,Y\in 2^\Theta, X\cap Y = A} m_1 (X) m_2 (Y)
                  ---------------------------------------------------
                                      1 - k_{12}
    '''
    if A == 0:
        return 0
    return sumXYcapA(n, m1, m2, A) / (1 - k_12(n, m1, m2))


def disjunctive_rule(n, m1, m2, A):
    '''
        Disjunctive Rule Of Combination
        The following is the definition:
        m(\emptyset)  = 0
        m(A) = \sum_{X,Y\in 2^\Theta, X\cap Y = A} m_1 (X) m_2 (Y)
    '''
    return sumXYcapA(n, m1, m2, A)


def murphy_rule(bel1, bel2, A):
    '''
        Murphy's rule of combination
        The following is a desription:
        Bel_M (A) = 0.5 [Bel_1 (A) + Bel_2 (A)]
    '''
    return 0.5 * (bel1(A) + bel2(A))


def smet_rule(n, m1, m2, A):
    '''
        Smets' rule of combination
        m(\emptyset)  = k_{12}
        m(A) =   \sum_{X,Y\in 2^\Theta, X\cap Y = A} m_1 (X) m_2 (Y)
                  ---------------------------------------------------
                                      1 - k_{12}
    '''
    if A == 0:
        return k_12(n, m1, m2)
    return sumXYcapA(n, m1, m2, A)


def yager_rule(n, m1, m2, A):
    '''
        Yagers rule of combination
        m(\emptyset) = 0
        m(A) = k_{12}(A)
        m(\Theta) = m_1(\Theta)
    '''
    if A == 0:
        return 0
    if A != n:
        return sumXYcapA(n, m1, m2, A)
    return m1(n)