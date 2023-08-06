import mvpoly.util.version as muv
import unittest

class TestCompareVersions(unittest.TestCase) :
    
    def test_compare_versions_equal_zero(self) :
        self.assertTrue(muv.compare_versions((0,0,0), (0,0,0)) == 0, 
                        "equal zero versions")

    def test_compare_versions_equal_nozero(self) :
        self.assertTrue(muv.compare_versions((7,0,3), (7,0,3)) == 0, 
                        "equal nonzero versions")

    def test_compare_versions_major(self) :
        self.assertTrue(muv.compare_versions((7,0,0), (6,6,6)) == 1, 
                        "major")

    def test_compare_versions_minor(self) :
        self.assertTrue(muv.compare_versions((0,7,0), (0,6,6)) == 1, 
                        "minor")

    def test_compare_versions_point(self) :
        self.assertTrue(muv.compare_versions((0,0,7), (0,0,6)) == 1, 
                        "point")

class TestAtLeast(unittest.TestCase) :

    def test_atleast_scipy(self) :
        self.assertTrue(muv.at_least('scipy', (0,0,1)),
                        "scipy version > 0.0.1")
        self.assertFalse(muv.at_least('scipy', (100,0,0)),
                        "scipy version < 100.0.0")

    def test_atleast_numpy(self) :
        self.assertTrue(muv.at_least('numpy', (0,0,1)),
                        "numpy version > 0.0.1")
        self.assertFalse(muv.at_least('numpy', (100,0,0)),
                        "numpy version > 100.0.0")

