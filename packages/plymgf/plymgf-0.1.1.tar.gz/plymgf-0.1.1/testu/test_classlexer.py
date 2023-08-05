#!/usr/bin/env python
# encoding: utf-8
# pylint: disable=too-many-public-methods
"""test_classlexer.py is units test for classlexer
@author: Vezin Aurelien
@license: CeCILL-B"""

import unittest
import os
import sys

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
        res = read_mgf(os.path.join(".", "testu", "data", "test.mgf"))
         
if __name__ == '__main__':
    unittest.main()

