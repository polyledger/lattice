# -*- coding: utf-8 -*-

"""
Test the optimize module.
"""

import unittest
import numpy as np
import pandas as pd
from lattice.optimize import allocate, retrieve_data

class TestOptimize(unittest.TestCase):
    """Test methods in the optimize module."""

    def test_retrieve_data(self):
        """Ensure that the data columns are ordered and named correctly"""
        dataframe = retrieve_data('2016-01-01')
        expected = ['BTC', 'ETH', 'BCH', 'XRP', 'LTC', 'XMR', 'ZEC', 'DASH',
                    'ETC', 'NEO']
        self.assertEqual(dataframe.columns.tolist(), expected)

    def test_allocate(self):
        """Ensure that the allocations for the given data are optimal."""
        risk_index = 1
        allocation = allocate(risk_index)

if __name__ == '__main__':
    unittest.main()
