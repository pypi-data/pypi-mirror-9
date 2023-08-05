#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=too-many-public-methods
"""test_classlexer.py is units test for classlexer
@author: Vezin Aurelien
@license: CeCILL-B"""

import unittest
import os

from plymgf.classlexer import read_mgf

class TestReadMGF(unittest.TestCase):
    """Class to test read_mgf function"""
    
    def setUp(self):
        """Run before each tests"""
        pass
    
    def tearDown(self):
        """Clear after each tests"""
        pass
    
    def test_10_read_mgf(self):
        """ test function of read_mgf"""
        res = read_mgf(os.path.join(".", "plymgf", "data", "test.mgf"))
        self.assertEqual(res["meta"], {'charges': [3, 2, 1]})
        self.assertEqual(res["ions"][2]["rtinseconds"], 603)
        self.assertEqual(res["ions"][3]["charges"], [3])
         
if __name__ == '__main__':
    unittest.main()

