#!/usr/bin/env python

"""
Created on May 15, 2012
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "May 15, 2012"

import unittest
import numpy as np

from pyhull.simplex import Simplex


class SimplexTest(unittest.TestCase):

    def setUp(self):
        coords = []
        coords.append([0, 0, 0])
        coords.append([0, 1, 0])
        coords.append([0, 0, 1])
        coords.append([1, 0, 0])
        self.simplex = Simplex(coords)

    def test_in_simplex(self):
        self.assertTrue(self.simplex.in_simplex([0.1, 0.1, 0.1]))
        self.assertFalse(self.simplex.in_simplex([0.6, 0.6, 0.6]))
        for i in range(10):
            coord = np.random.random_sample(size=3) / 3
            self.assertTrue(self.simplex.in_simplex(coord))

    def test_2dtriangle(self):
        s = Simplex([[0, 1], [1, 1], [1, 0]])
        np.testing.assert_almost_equal(s.bary_coords([0.5, 0.5]), [0.5, 0, 0.5])
        np.testing.assert_almost_equal(s.bary_coords([0.5, 1]), [0.5, 0.5, 0])
        np.testing.assert_almost_equal(s.bary_coords([0.5, 0.75]), [0.5, 0.25, 0.25])
        np.testing.assert_almost_equal(s.bary_coords([0.75, 0.75]), [0.25, 0.5, 0.25])

        s = Simplex([[1, 1], [1, 0]])
        self.assertRaises(ValueError, s.bary_coords, [0.5, 0.5])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
