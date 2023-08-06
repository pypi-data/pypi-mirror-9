#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Jonathan S. Prieto
# @Date:   2015-02-17 15:31:51
# @Last Modified time: 2015-03-03 16:26:31

import unittest
from evidence.theory import dst
from evidence.tests.assets import INPUT

class Test(unittest.TestCase):

    def test_theory_dst_bba_bel(self):
        ans = []
        with open(INPUT['bel.txt'], 'r') as f:
            ans = map(lambda x: x.strip(), f.readlines())
            ans.reverse()

        def ANS():
            return ans.pop(-1)

        with open(INPUT['bba.txt'], 'r') as f:
            N = int(f.readline())
            self.assertEqual(N, float(ANS()))
            for _ in range(N):
                n = int(f.readline())
                self.assertEqual(n, int(ANS()))
                bba = []
                for i in range(1 << n):
                    bba += [float(f.readline())]
                for i in range(1 << n):
                    self.assertAlmostEqual(dst.Bel(m=bba, A=i), float(ANS()))

    def test_theory_dst_bel_bba(self):
        ans = []
        with open(INPUT['bba.txt'], 'r') as f:
            ans = map(lambda x: x.strip(), f.readlines())
            ans.reverse()

        def ANS():
            return ans.pop(-1)

        with open(INPUT['bel.txt'], 'r') as f:
            N = int(f.readline())
            self.assertEqual(N, float(ANS()))
            for _ in range(N):
                n = int(f.readline())
                self.assertEqual(n, int(ANS()))
                bel = []
                for i in range(1 << n):
                    bel += [float(f.readline())]
                for i in range(1 << n):
                    self.assertAlmostEqual(dst.m(Bel=bel, A=i), float(ANS()))


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()
