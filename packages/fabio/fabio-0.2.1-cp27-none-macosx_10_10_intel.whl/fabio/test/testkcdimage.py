#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Test for Nonius Kappa CCD cameras.

"""

from __future__ import print_function, with_statement, division, absolute_import
import unittest
import sys
import os
try:
    from .utilstest import UtilsTest
except (ValueError, SystemError):
    from utilstest import UtilsTest

logger = UtilsTest.get_logger(__file__)
fabio = sys.modules["fabio"]
from fabio.kcdimage     import kcdimage
from fabio.edfimage     import edfimage
from fabio.openimage    import openimage


class testkcd(unittest.TestCase):
    """basic test"""
    kcdfilename = 'i01f0001.kcd'
    edffilename = 'i01f0001.edf'
    results = """i01f0001.kcd   625 576  96  66814.0 195.3862972   243.58150990245315"""

    def setUp(self):
        """Download files"""
        self.fn = {}
        for i in ["i01f0001.kcd", "i01f0001.edf"]:
            self.fn[i] = UtilsTest.getimage(i + ".bz2")[:-4]
        for i in self.fn:
            assert os.path.exists(self.fn[i])

    def test_read(self):
        """ check we can read kcd images"""
        vals = self.results.split()
        name = vals[0]
        dim1, dim2 = [int(x) for x in vals[1:3]]
        mini, maxi, mean, stddev = [float(x) for x in vals[3:]]
        obj = openimage(self.fn[self.kcdfilename])
        self.assertAlmostEqual(mini, obj.getmin(), 4, "getmin")
        self.assertAlmostEqual(maxi, obj.getmax(), 4, "getmax")
        self.assertAlmostEqual(mean, obj.getmean(), 4, "getmean")
        self.assertAlmostEqual(stddev, obj.getstddev(), 4, "getstddev")
        self.assertEqual(dim1, obj.dim1, "dim1")
        self.assertEqual(dim2, obj.dim2, "dim2")

    def test_same(self):
        """ see if we can read kcd images and if they are the same as the EDF """
        kcd = kcdimage()
        kcd.read(self.fn[self.kcdfilename])
        edf = fabio.open(self.fn[self.edffilename])
        diff = (kcd.data.astype("int32") - edf.data.astype("int32"))
        self.assertAlmostEqual(abs(diff).sum(dtype=int), 0, 4)


def test_suite_all_kcd():
    testSuite = unittest.TestSuite()
    testSuite.addTest(testkcd("test_read"))
    testSuite.addTest(testkcd("test_same"))
    return testSuite

if __name__ == '__main__':
    mysuite = test_suite_all_kcd()
    runner = unittest.TextTestRunner()
    runner.run(mysuite)
