#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 12:20:27 CEST
# File:    kpts_abinit.py
"""Module containing the TestCase for Abinit k-point generation"""

import sys
sys.path.insert(0, '../')
import z2pack

import unittest
from common import *

class KptsAbinitTestCase(unittest.TestCase):
    """TestCase for the z2pack.fp.kpts.abinit function"""

    def test1(self):
        """test basic functionality"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [0.2, 0, 0.5], [0.2, 0.9, 0.5], [0.2, 1, 0.5], 10),
            '\nkptopt -1\nndivk 9\nkptbounds 0.2 0 0.5 \n0.2 0.9 0.5 \n')

    def test2(self):
        """test basic functionality"""
        self.assertEqual(
            z2pack.fp.kpts.abinit(
                [0., 0.6, 0.5], [0.99, 0.6, 0.5], [1, 0.6, 0.5], 100),
            '\nkptopt -1\nndivk 99\nkptbounds 0.0 0.6 0.5 \n0.99 0.6 0.5 \n')

    def test3(self):
        """test for ValueError with wrong dimension of point"""
        self.assertRaises(
            ValueError,
            z2pack.fp.kpts.abinit,
            [1, 2], [0., 1., 2.], [5., 2., 6.], 10)

    def test4(self):
        """test for TypeError with non-int number of points"""
        self.assertRaises(
            TypeError,
            z2pack.fp.kpts.abinit,
            [0.2, 0, 0.5], [0.2, 0.9, 0.5], [0.2, 1, 0.5], 'str')


if __name__ == "__main__":
    unittest.main()
